import json
import re
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from ..models.memory import MemoryMeta
from ..models.conversation import Conversation

MEMORY_DIR = Path("./memory_files")
MEMORY_DIR.mkdir(exist_ok=True)

def get_kv_file(app_key: str) -> Path:
    return MEMORY_DIR / f"memory_kv_store_{app_key}.md"

def get_digest_file(app_key: str) -> Path:
    return MEMORY_DIR / f"memory_digest_{app_key}.md"

async def load_memory(app_key: str) -> str:
    """加载记忆内容注入System Prompt"""
    kv_file = get_kv_file(app_key)
    digest_file = get_digest_file(app_key)
    parts = []

    if kv_file.exists():
        content = kv_file.read_text(encoding="utf-8").strip()
        if content:
            parts.append(f"## 用户事实记忆\n{content}")

    if digest_file.exists():
        content = digest_file.read_text(encoding="utf-8").strip()
        if content:
            parts.append(f"## 行为摘要\n{content}")

    return "\n\n".join(parts)

def _load_kv_store(app_key: str) -> dict:
    """加载KV存储"""
    kv_file = get_kv_file(app_key)
    kv_data = {}
    if kv_file.exists():
        for line in kv_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if ": " in line and not line.startswith("#"):
                key, _, value = line.partition(": ")
                kv_data[key.strip()] = value.strip()
    return kv_data

def _save_kv_store(app_key: str, kv_data: dict):
    """保存KV存储"""
    kv_file = get_kv_file(app_key)
    lines = [f"# 事实记忆 - 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    for key, value in kv_data.items():
        lines.append(f"{key}: {value}")
    kv_file.write_text("\n".join(lines), encoding="utf-8")

def _extract_facts_from_dialog(user_msg: str, ai_resp: str) -> dict:
    """从对话中提取事实记忆（KV键值对）"""
    facts = {}
    combined = f"{user_msg}\n{ai_resp}"

    # 姓名/昵称
    name_patterns = [
        r"(?:我叫|我是|名字是|姓名[是为：:])[\s]*([^\s，,。.！!？?]{2,6})",
        r"(?:叫我|称呼我[为叫作]?)[\s]*([^\s，,。.！!？?]{2,6})",
    ]
    for p in name_patterns:
        m = re.search(p, combined)
        if m:
            facts["用户姓名"] = m.group(1)
            break

    # 职业
    job_patterns = [
        r"(?:我是|我的职业是|从事|工作是)[\s]*([^\s，,。.！!？?]{2,10}(?:师|员|官|长|手|者|生|工))",
        r"(?:我是一名|我是一个)[\s]*([^\s，,。.！!？?的]{2,8})",
    ]
    for p in job_patterns:
        m = re.search(p, combined)
        if m:
            facts["用户职业"] = m.group(1)
            break

    # 编程语言偏好
    lang_patterns = [
        r"(?:喜欢|常用|使用|偏好|主要用)[\s]*(Python|Java|Go|C\+\+|JavaScript|TypeScript|Rust|PHP|Ruby|Swift|Kotlin)",
        r"(Python|Java|Go|C\+\+|JavaScript|TypeScript|Rust|PHP|Ruby|Swift|Kotlin)[\s]*(?:程序员|开发者|工程师)",
    ]
    for p in lang_patterns:
        m = re.search(p, combined, re.IGNORECASE)
        if m:
            facts["偏好语言"] = m.group(1)
            break

    # 公司
    company_patterns = [
        r"(?:在|就职于|供职于)[\s]*([^\s，,。.！!？?]{2,15}(?:公司|科技|集团|企业|有限|股份))",
    ]
    for p in company_patterns:
        m = re.search(p, combined)
        if m:
            facts["所在公司"] = m.group(1)
            break

    return facts

async def save_conversation(db: Session, app_key: str, user_message: str, ai_response: str):
    """保存对话记录"""
    # 获取当前轮次
    last = db.query(Conversation).filter(
        Conversation.app_key == app_key
    ).order_by(Conversation.round_number.desc()).first()

    round_number = (last.round_number + 1) if last else 1

    conv = Conversation(
        app_key=app_key,
        round_number=round_number,
        user_message=user_message,
        ai_response=ai_response
    )
    db.add(conv)
    db.commit()
    return round_number

async def should_process_memory(db: Session, app_key: str, current_round: int):
    """检查是否需要处理记忆"""
    try:
        with open("agent_config.json", "r") as f:
            config = json.load(f)
    except Exception:
        config = {}

    threshold = config.get("memory_processing", {}).get("rounds_threshold", 5)

    meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not meta:
        meta = MemoryMeta(
            app_key=app_key,
            last_processed_round=0,
            kv_file_path=str(get_kv_file(app_key)),
            digest_file_path=str(get_digest_file(app_key))
        )
        db.add(meta)
        db.commit()

    if current_round - meta.last_processed_round >= threshold:
        result = await process_memory(db, app_key, meta.last_processed_round, current_round)
        meta.last_processed_round = current_round
        meta.kv_file_path = str(get_kv_file(app_key))
        meta.digest_file_path = str(get_digest_file(app_key))
        db.commit()
        return result

    return None

async def process_memory(db: Session, app_key: str, from_round: int, to_round: int) -> dict:
    """处理双层记忆"""
    # 获取待处理的对话
    conversations = db.query(Conversation).filter(
        Conversation.app_key == app_key,
        Conversation.round_number > from_round,
        Conversation.round_number <= to_round
    ).order_by(Conversation.round_number.asc()).all()

    if not conversations:
        return {"factMemory": {}, "digestMemory": ""}

    # === 事实记忆层（KV Store）===
    kv_data = _load_kv_store(app_key)
    for conv in conversations:
        new_facts = _extract_facts_from_dialog(conv.user_message, conv.ai_response)
        kv_data.update(new_facts)  # UPSERT：新信息覆盖旧信息

    _save_kv_store(app_key, kv_data)

    # === 行为摘要层（Text Memory）===
    digest_file = get_digest_file(app_key)
    existing_digest = ""
    if digest_file.exists():
        existing_digest = digest_file.read_text(encoding="utf-8").strip()

    # 构建本批次对话文本
    dialog_text = "\n".join([
        f"[轮{c.round_number}] 用户: {c.user_message[:100]}\n[轮{c.round_number}] AI: {c.ai_response[:200]}"
        for c in conversations
    ])

    # 生成递归摘要
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    round_range = f"第{conversations[0].round_number}-{conversations[-1].round_number}轮"

    # 检测是否需要跨层引用（简单规则检测）
    needs_history = any(
        keyword in (c.user_message + c.ai_response).lower()
        for c in conversations
        for keyword in ["之前", "上次", "刚才", "前面", "历史", "记得吗", "你说过"]
    )
    cross_layer_tag = " [跨层引用]" if needs_history else ""

    new_digest_entry = (
        f"\n---\n"
        f"**时间**: {timestamp} | **轮次**: {round_range}{cross_layer_tag}\n"
        f"**行为摘要**: 用户进行了{len(conversations)}轮对话。"
    )

    # 提取关键行为
    actions = []
    for conv in conversations:
        user_msg = conv.user_message
        if any(k in user_msg for k in ["帮我", "请", "能否", "如何", "怎么"]):
            actions.append(f"寻求帮助: {user_msg[:50]}")
        elif any(k in user_msg for k in ["谢谢", "感谢", "好的", "明白了"]):
            actions.append("确认/感谢")

    if actions:
        new_digest_entry += f" 主要行为: {'; '.join(set(actions[:3]))}"

    # 递归摘要：如果已有摘要过长，对旧摘要进行压缩
    if len(existing_digest) > 3000:
        lines = existing_digest.split("\n---\n")
        # 保留最近5条，压缩旧的
        if len(lines) > 6:
            old_summary = f"\n---\n[早期摘要压缩] 共{len(lines)-5}条历史记录已归档"
            existing_digest = old_summary + "\n---\n" + "\n---\n".join(lines[-5:])

    full_digest = existing_digest + new_digest_entry
    digest_file.write_text(full_digest, encoding="utf-8")

    result = {
        "factMemory": kv_data,
        "digestMemory": full_digest
    }
    return result

async def process_memory_manual(db: Session, app_key: str, user_message: str, ai_response: str) -> dict:
    """手动触发记忆处理接口（每次对话后调用）"""
    current_round = await save_conversation(db, app_key, user_message, ai_response)
    memory_result = await should_process_memory(db, app_key, current_round)

    if memory_result:
        return memory_result

    # 未达到处理阈值，返回当前记忆状态
    kv_data = _load_kv_store(app_key)
    digest_file = get_digest_file(app_key)
    digest = digest_file.read_text(encoding="utf-8") if digest_file.exists() else ""

    return {
        "factMemory": kv_data,
        "digestMemory": digest
    }

async def get_memory_files(app_key: str) -> dict:
    """获取记忆文件内容（供管理员查看）"""
    kv_file = get_kv_file(app_key)
    digest_file = get_digest_file(app_key)

    return {
        "app_key": app_key,
        "kv_content": kv_file.read_text(encoding="utf-8") if kv_file.exists() else "",
        "digest_content": digest_file.read_text(encoding="utf-8") if digest_file.exists() else "",
        "kv_file": str(kv_file),
        "digest_file": str(digest_file)
    }

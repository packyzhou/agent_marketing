import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from ..models.memory import MemoryMeta

MEMORY_DIR = Path("./memory_files")
MEMORY_DIR.mkdir(exist_ok=True)

async def load_memory(app_key: str) -> str:
    """加载记忆内容"""
    kv_file = MEMORY_DIR / f"memory_kv_store_{app_key}.md"
    digest_file = MEMORY_DIR / f"memory_digest_{app_key}.md"

    memory_content = []

    if kv_file.exists():
        with open(kv_file, 'r', encoding='utf-8') as f:
            memory_content.append("## 事实记忆 (Facts)\n" + f.read())

    if digest_file.exists():
        with open(digest_file, 'r', encoding='utf-8') as f:
            memory_content.append("## 行为摘要 (Digest)\n" + f.read())

    return "\n\n".join(memory_content) if memory_content else ""

async def should_process_memory(db: Session, app_key: str, messages: list):
    """检查是否需要处理记忆"""
    with open("agent_config.json", 'r') as f:
        config = json.load(f)

    threshold = config["memory_processing"]["rounds_threshold"]

    meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not meta:
        meta = MemoryMeta(app_key=app_key, last_processed_round=0)
        db.add(meta)
        db.commit()

    current_round = len(messages) // 2

    if current_round - meta.last_processed_round >= threshold:
        await process_memory(db, app_key, messages)
        meta.last_processed_round = current_round
        db.commit()

async def process_memory(db: Session, app_key: str, messages: list):
    """处理记忆提取"""
    # 提取事实记忆
    facts = await extract_facts(messages)
    await save_facts(app_key, facts)

    # 提取行为摘要
    digest = await extract_digest(messages)
    await save_digest(app_key, digest)

async def extract_facts(messages: list) -> dict:
    """从对话中提取事实记忆（KV键值对）"""
    facts = {}
    for msg in messages:
        content = msg.get("content", "")
        # 简化实现：实际应调用LLM提取
        if "名字" in content or "姓名" in content:
            facts["user_name"] = "提取的名字"
        if "电话" in content or "手机" in content:
            facts["phone"] = "提取的电话"

    return facts

async def save_facts(app_key: str, facts: dict):
    """保存事实记忆到KV存储"""
    kv_file = MEMORY_DIR / f"memory_kv_store_{app_key}.md"

    existing_facts = {}
    if kv_file.exists():
        with open(kv_file, 'r', encoding='utf-8') as f:
            for line in f:
                if ": " in line:
                    key, value = line.strip().split(": ", 1)
                    existing_facts[key] = value

    existing_facts.update(facts)

    with open(kv_file, 'w', encoding='utf-8') as f:
        for key, value in existing_facts.items():
            f.write(f"{key}: {value}\n")

async def extract_digest(messages: list) -> str:
    """从对话中提取行为摘要"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = f"[{timestamp}] 用户进行了对话交互"

    # 简化实现：实际应调用LLM生成摘要
    if len(messages) > 0:
        last_msg = messages[-1].get("content", "")
        summary = f"[{timestamp}] {last_msg[:50]}..."

    return summary

async def save_digest(app_key: str, digest: str):
    """保存行为摘要"""
    digest_file = MEMORY_DIR / f"memory_digest_{app_key}.md"

    with open(digest_file, 'a', encoding='utf-8') as f:
        f.write(digest + "\n")

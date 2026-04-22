import asyncio
import json
import re
from datetime import timezone
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from ..models.memory import MemoryMeta
from ..models.conversation import Conversation

MEMORY_DIR = Path("./memory_files")
MEMORY_DIR.mkdir(exist_ok=True)

_AGENT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "agent_config.json"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def get_kv_file(app_key: str) -> Path:
    return MEMORY_DIR / f"memory_kv_store_{app_key}.md"


def get_digest_file(app_key: str) -> Path:
    return MEMORY_DIR / f"memory_digest_{app_key}.md"


def get_domain_file(app_key: str) -> Path:
    return MEMORY_DIR / f"memory_domain_{app_key}.md"


def _read_domain(path: Path) -> dict:
    """领域记忆以 JSON 形式存储，返回 {} 以便新增二级分类扩展。"""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {"workSkill": text}


def _write_domain(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_memory_config() -> dict:
    try:
        return json.loads(_AGENT_CONFIG_PATH.read_text(encoding="utf-8")).get(
            "memory_processing", {}
        )
    except Exception:
        return {}


def _extract_json(text: str) -> dict | None:
    """Extract a JSON object from AI response, tolerating markdown code fences."""
    text = text.strip()
    # Strip markdown code fence if present
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    # Find the outermost { … } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------------------
# Public read interface (used by chat proxy to inject memory into messages)
# ---------------------------------------------------------------------------


async def load_memory(app_key: str, db: Optional[Session] = None) -> str:
    """Assemble memory context to inject as a system message.

    包含两类记忆：
    - 永久记忆：kv_file（事实记忆）/ digest_file（行为摘要）/ domain_file（领域记忆）
    - 临时记忆：尚未被后台蒸馏的 tb_conversation 对话记录（db 可用时）
    """
    parts = []
    kv_file = get_kv_file(app_key)
    if kv_file.exists():
        content = kv_file.read_text(encoding="utf-8").strip()
        if content:
            parts.append(f"## 用户事实记忆\n{content}")

    digest_file = get_digest_file(app_key)
    if digest_file.exists():
        content = digest_file.read_text(encoding="utf-8").strip()
        if content:
            parts.append(f"## 行为摘要\n{content}")

    domain_file = get_domain_file(app_key)
    domain_data = _read_domain(domain_file)
    if domain_data:
        work_skill = domain_data.get("workSkill")
        if work_skill:
            if isinstance(work_skill, (list, dict)):
                work_skill_text = json.dumps(work_skill, ensure_ascii=False, indent=2)
            else:
                work_skill_text = str(work_skill).strip()
            if work_skill_text:
                parts.append(f"## 领域记忆 - 工作技能\n{work_skill_text}")

    temp_text = _load_temporary_memory(db, app_key) if db is not None else ""
    if temp_text:
        parts.append(f"## 临时对话记忆\n{temp_text}")
    print(
        f"------------------------------------记忆1--------------------------------------------"
    )
    print("\n".join(parts))
    print(
        f"------------------------------------记忆2--------------------------------------------"
    )
    return "\n\n".join(parts)


def _load_temporary_memory(db: Session, app_key: str) -> str:
    """读取 tb_conversation 中尚未被后台蒸馏的对话，作为临时记忆。"""
    try:
        rows = (
            db.query(Conversation)
            .filter(Conversation.app_key == app_key)
            .order_by(Conversation.round_number.asc())
            .all()
        )
    except Exception:
        return ""
    if not rows:
        return ""

    lines = []
    for conv in rows:
        ts = ""
        if conv.created_at:
            try:
                ts = (
                    conv.created_at.replace(tzinfo=timezone.utc)
                    .astimezone(tz=None)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception:
                ts = ""
        prefix = f"[{ts}] " if ts else ""
        user_msg = (conv.user_message or "").strip()
        ai_msg = (conv.ai_response or "").strip()
        if user_msg:
            lines.append(f"{prefix}用户: {user_msg}")
        if ai_msg:
            lines.append(f"{prefix}助手: {ai_msg}")
    return "\n".join(lines)


async def get_memory_files(app_key: str) -> dict:
    """Return raw file contents (used by admin API)."""
    kv_file = get_kv_file(app_key)
    digest_file = get_digest_file(app_key)
    domain_file = get_domain_file(app_key)
    return {
        "app_key": app_key,
        "kv_content": kv_file.read_text(encoding="utf-8") if kv_file.exists() else "",
        "digest_content": (
            digest_file.read_text(encoding="utf-8") if digest_file.exists() else ""
        ),
        "domain_content": (
            domain_file.read_text(encoding="utf-8") if domain_file.exists() else ""
        ),
        "kv_file": str(kv_file),
        "digest_file": str(digest_file),
        "domain_file": str(domain_file),
    }


# ---------------------------------------------------------------------------
# AI memory processing (background task)
# ---------------------------------------------------------------------------


async def _process_memory_with_ai(app_key: str) -> None:
    """Background coroutine: run AI memory extraction when enough conversations exist.

    Creates its own DB session so it can safely run after the chat request
    has already returned and the request-scoped session has been closed.
    """
    from ..core.database import SessionLocal
    from .system_llm import system_chat_completion

    db: Session = SessionLocal()
    try:
        config = _load_memory_config()
        if not config.get("enable_auto_processing", True):
            return

        digest_rounds = int(config.get("digest_rounds", 10))
        prompt_type = (config.get("prompt_type") or "").strip()

        # 1. 读取 app_key 对应的全部对话，不足 digest_rounds 则跳过
        convs = (
            db.query(Conversation)
            .filter(Conversation.app_key == app_key)
            .order_by(Conversation.round_number.asc())
            .all()
        )

        print(
            f"appkey:{app_key} | len(convs):{len(convs)} | digest_rounds:{digest_rounds}"
        )
        if len(convs) < digest_rounds:
            return

        dialogs = [
            {
                "time": (
                    c.created_at.replace(tzinfo=timezone.utc)
                    .astimezone(tz=None)
                    .strftime("%Y-%m-%d %H:%M:%S")
                    if c.created_at
                    else ""
                ),
                "user": c.user_message,
                "ai": c.ai_response,
            }
            for c in convs
        ]

        # 计算本批次对话覆盖的时长（首条到末条的时间差），用于累计对话总时长
        batch_duration_seconds = 0
        try:
            timestamps = [c.created_at for c in convs if c.created_at]
            if len(timestamps) >= 2:
                batch_duration_seconds = max(
                    0,
                    int((max(timestamps) - min(timestamps)).total_seconds()),
                )
        except Exception:
            batch_duration_seconds = 0

        # 读取完毕后立即删除本次对话记录，避免重复处理
        conv_ids = [c.id for c in convs]
        db.query(Conversation).filter(Conversation.id.in_(conv_ids)).delete(
            synchronize_session=False
        )
        db.commit()

        # 2. 读取记忆元数据，确保记录存在，并读取文件内容
        meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
        if not meta:
            meta = MemoryMeta(
                app_key=app_key,
                last_processed_round=0,
                kv_file_path=str(get_kv_file(app_key)),
                digest_file_path=str(get_digest_file(app_key)),
                domain_file_path=str(get_domain_file(app_key)),
                total_duration_seconds=0,
            )
            db.add(meta)
            db.commit()

        # 累加对话总时长
        if batch_duration_seconds > 0:
            meta.total_duration_seconds = (
                meta.total_duration_seconds or 0
            ) + batch_duration_seconds
            db.commit()

        kv_path = Path(meta.kv_file_path) if meta.kv_file_path else get_kv_file(app_key)
        digest_path = (
            Path(meta.digest_file_path)
            if meta.digest_file_path
            else get_digest_file(app_key)
        )
        domain_path = (
            Path(meta.domain_file_path)
            if meta.domain_file_path
            else get_domain_file(app_key)
        )

        existing_fact = (
            kv_path.read_text(encoding="utf-8").strip() if kv_path.exists() else ""
        )
        existing_digest = (
            digest_path.read_text(encoding="utf-8").strip()
            if digest_path.exists()
            else ""
        )
        existing_domain = _read_domain(domain_path)
        existing_work_skill = existing_domain.get("workSkill", "")

        # 3. 组装 JSON 数据集合发送给系统模型
        payload = {
            "dialogs": dialogs,
            "factMemory": existing_fact,
            "digestMemory": existing_digest,
            "domain_workSkill": existing_work_skill,
        }
        messages = [
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ]

        print(f"记忆请求:{payload}")
        result_text = ""
        async for chunk in system_chat_completion(
            messages, stream=False, db=db, prompt_type=prompt_type
        ):
            choices = chunk.get("choices", [])
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                if isinstance(msg, dict):
                    result_text = msg.get("content", result_text)

        if not result_text:
            return

        # 4. 解析返回值，将 factMemory / digestMemory 写回对应文件
        result = _extract_json(result_text)
        print(f"记忆结果:{result}")
        if not result:
            return

        fact_memory = result.get("factMemory")
        if isinstance(fact_memory, str) and fact_memory.strip():
            kv_path.parent.mkdir(parents=True, exist_ok=True)
            kv_path.write_text(fact_memory.strip(), encoding="utf-8")
        elif isinstance(fact_memory, dict) and fact_memory:
            kv_path.parent.mkdir(parents=True, exist_ok=True)
            kv_path.write_text(
                json.dumps(fact_memory, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        digest_memory = result.get("digestMemory")
        if isinstance(digest_memory, list):
            digest_text = "\n".join(str(item) for item in digest_memory if item)
        elif isinstance(digest_memory, str):
            digest_text = digest_memory.strip()
        else:
            digest_text = ""
        if digest_text:
            digest_path.parent.mkdir(parents=True, exist_ok=True)
            digest_path.write_text(digest_text, encoding="utf-8")

        # 领域记忆 - 工作技能：模型以 domain_workSkill 字段返回
        domain_work_skill = result.get("domain_workSkill")
        if domain_work_skill not in (None, "", [], {}):
            existing_domain["workSkill"] = domain_work_skill
            _write_domain(domain_path, existing_domain)

        # 更新元数据文件路径
        meta.kv_file_path = str(kv_path)
        meta.digest_file_path = str(digest_path)
        meta.domain_file_path = str(domain_path)
        db.commit()

    except Exception:
        # Memory processing must never crash the chat flow
        pass
    finally:
        db.close()


def schedule_memory_processing(app_key: str) -> None:
    """Fire-and-forget: schedule AI memory processing as a background asyncio task.

    Safe to call from both sync and async contexts as long as an event loop
    is already running (which is always true inside a FastAPI request handler).
    """
    asyncio.create_task(_process_memory_with_ai(app_key))

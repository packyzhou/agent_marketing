"""Synchronous DB access for agent flow config + plugin refs.

All functions take an explicit Session. Async callers should wrap these in
run_blocking() with a fresh SessionLocal (see service.py).
"""

from typing import List, Optional

from sqlalchemy import asc
from sqlalchemy.orm import Session

from ...models.agent_flow import AgentFlowConfig, AgentPluginRef


# --------------------------------------------------------------------------- #
# Flow config
# --------------------------------------------------------------------------- #


def get_flow_config(db: Session, app_key: str) -> Optional[AgentFlowConfig]:
    return (
        db.query(AgentFlowConfig)
        .filter(AgentFlowConfig.app_key == app_key)
        .first()
    )


def get_flow_config_by_id(db: Session, config_id: int) -> Optional[AgentFlowConfig]:
    return db.query(AgentFlowConfig).filter(AgentFlowConfig.id == config_id).first()


def upsert_flow_config(db: Session, app_key: str, fields: dict) -> AgentFlowConfig:
    config = get_flow_config(db, app_key)
    if config is None:
        config = AgentFlowConfig(app_key=app_key)
        db.add(config)
    for key, value in fields.items():
        if hasattr(config, key) and key not in {"id", "app_key", "created_at"}:
            setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


def delete_flow_config(db: Session, app_key: str) -> bool:
    config = get_flow_config(db, app_key)
    if not config:
        return False
    db.query(AgentPluginRef).filter(AgentPluginRef.app_key == app_key).delete(
        synchronize_session=False
    )
    db.delete(config)
    db.commit()
    return True


# --------------------------------------------------------------------------- #
# Plugin refs
# --------------------------------------------------------------------------- #


def list_plugins(db: Session, app_key: str) -> List[AgentPluginRef]:
    return (
        db.query(AgentPluginRef)
        .filter(AgentPluginRef.app_key == app_key)
        .order_by(asc(AgentPluginRef.sort_order), asc(AgentPluginRef.id))
        .all()
    )


def list_enabled_plugins(db: Session, app_key: str) -> List[AgentPluginRef]:
    return [p for p in list_plugins(db, app_key) if p.enabled]


def get_plugin(db: Session, plugin_id: int) -> Optional[AgentPluginRef]:
    return db.query(AgentPluginRef).filter(AgentPluginRef.id == plugin_id).first()


def create_plugin(db: Session, fields: dict) -> AgentPluginRef:
    plugin = AgentPluginRef(**fields)
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return plugin


def update_plugin(db: Session, plugin_id: int, fields: dict) -> Optional[AgentPluginRef]:
    plugin = get_plugin(db, plugin_id)
    if not plugin:
        return None
    for key, value in fields.items():
        if hasattr(plugin, key) and key not in {"id", "created_at"}:
            setattr(plugin, key, value)
    db.commit()
    db.refresh(plugin)
    return plugin


def delete_plugin(db: Session, plugin_id: int) -> bool:
    plugin = get_plugin(db, plugin_id)
    if not plugin:
        return False
    db.delete(plugin)
    db.commit()
    return True

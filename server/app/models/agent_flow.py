from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class AgentFlowConfig(Base):
    """Agent 编排配置（appKey 粒度，1:1）。

    通过 OpenAI Agents SDK 动态读取字段（name / instructions 等）生成 Agent 实例。
    mode 决定多 Agent 协作方式：
      - "single"   : 单 Agent
      - "tool"     : agent-as-tool 并行调用模式
      - "handoff"  : handoff 交接模式
    """

    __tablename__ = "tb_agent_flow_config"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_key = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(150), nullable=False, default="Agent")
    instructions = Column(Text, nullable=True)
    mode = Column(String(20), nullable=False, default="single")
    model = Column(String(100), nullable=True)
    max_turns = Column(Integer, nullable=False, default=10)
    # 协作模式下子 Agent 的 JSON 定义：[{"name","instructions","model","plugin_ids":[...]}]
    sub_agents = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AgentPluginRef(Base):
    """Agent 插件关联表（flow_config 1:n plugin）。

    每行即「某编排配置下挂载的一个 MCP 插件」，同时承载插件本体（脚本/配置），
    供「插件编辑器」在线编辑、调试与保存。
      - plugin_type = "builtin" : 使用 app/agent/plugins 下内置脚本（builtin_key 指定）
      - plugin_type = "custom"  : 使用 script_content 内联的 MCP stdio 脚本
    """

    __tablename__ = "tb_agent_plugin_ref"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    flow_config_id = Column(BigInteger, nullable=False, index=True)
    app_key = Column(String(64), nullable=False, index=True)
    plugin_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    plugin_type = Column(String(20), nullable=False, default="custom")
    builtin_key = Column(String(100), nullable=True)
    script_content = Column(Text, nullable=True)
    # 启动 MCP server 所需的额外参数 / 环境变量（JSON）
    config_json = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

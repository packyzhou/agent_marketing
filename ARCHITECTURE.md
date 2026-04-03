# 项目架构说明

## 整体架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│   Nginx     │─────▶│   FastAPI   │
│  (Vue3 SPA) │      │  (Frontend) │      │  (Backend)  │
└─────────────┘      └─────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │   MySQL     │
                                           │  Database   │
                                           └─────────────┘
```

## 目录结构详解

### 后端 (server/)

```
server/
├── app/
│   ├── api/                    # API路由层
│   │   ├── admin/             # 管理员接口
│   │   │   ├── provider.py    # 供应商管理
│   │   │   └── tenant.py      # 租户管理（管理员视图）
│   │   ├── user/              # 用户接口
│   │   │   ├── auth.py        # 认证（登录/注册）
│   │   │   ├── tenant.py      # 租户配置
│   │   │   ├── stats.py       # 统计数据
│   │   │   └── schemas.py     # 数据模型
│   │   └── proxy/             # AI中转接口
│   │       └── chat.py        # 对话中转
│   ├── core/                  # 核心模块
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── security.py        # 安全（JWT/密码）
│   │   ├── snowflake.py       # ID生成器
│   │   └── deps.py            # 依赖注入
│   ├── models/                # 数据模型（ORM）
│   │   ├── user.py            # 用户/分组
│   │   ├── tenant.py          # 租户
│   │   ├── provider.py        # 供应商
│   │   ├── token.py           # Token统计
│   │   └── memory.py          # 记忆元数据
│   ├── services/              # 业务逻辑层
│   │   ├── llm_base.py        # LLM基类
│   │   ├── llm_factory.py     # LLM工厂
│   │   ├── token_service.py   # Token统计服务
│   │   └── memory_service.py  # 记忆处理服务
│   └── main.py                # 应用入口
├── agent_config.json          # 全局配置
├── requirements.txt           # Python依赖
└── Dockerfile                 # Docker构建文件
```

### 前端 (web/)

```
web/
├── src/
│   ├── views/                 # 页面组件
│   │   ├── Login.vue          # 登录页
│   │   ├── admin/             # 管理员页面
│   │   │   ├── Layout.vue     # 管理员布局
│   │   │   ├── Tenants.vue    # 租户管理
│   │   │   └── Providers.vue  # 供应商管理
│   │   └── user/              # 用户页面
│   │       ├── Layout.vue     # 用户布局
│   │       ├── Dashboard.vue  # 数据中心
│   │       └── Tenants.vue    # 租户配置
│   ├── router/                # 路由配置
│   │   └── index.js
│   ├── api/                   # API封装
│   │   └── request.js         # Axios配置
│   ├── App.vue                # 根组件
│   └── main.js                # 应用入口
├── index.html                 # HTML模板
├── package.json               # Node依赖
├── vite.config.js             # Vite配置
├── tailwind.config.js         # Tailwind配置
├── nginx.conf                 # Nginx配置
└── Dockerfile                 # Docker构建文件
```

## 数据流

### 1. 用户认证流程

```
用户输入账号密码
    ↓
POST /api/auth/login
    ↓
验证用户名密码
    ↓
生成JWT Token
    ↓
返回Token给前端
    ↓
前端存储Token到localStorage
    ↓
后续请求携带Token
```

### 2. AI对话中转流程

```
客户端请求
    ↓
POST /api/proxy/chat/completions
    ↓
验证AppKey
    ↓
加载记忆文件
    ↓
注入System Prompt
    ↓
调用第三方AI
    ↓
流式返回结果
    ↓
统计Token消耗
    ↓
检查是否需要处理记忆
```

### 3. 记忆处理流程

```
对话轮次达到阈值（5轮）
    ↓
异步触发记忆处理
    ↓
提取事实记忆（KV）
    ↓
保存到 memory_kv_store_<AppKey>.md
    ↓
提取行为摘要（Text）
    ↓
追加到 memory_digest_<AppKey>.md
    ↓
更新处理轮次
```

## 核心技术选型

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 编程语言 |
| FastAPI | 0.109 | Web框架 |
| SQLAlchemy | 2.0 | ORM |
| PyMySQL | 1.1 | MySQL驱动 |
| python-jose | 3.3 | JWT处理 |
| passlib | 1.7 | 密码加密 |
| httpx | 0.26 | HTTP客户端 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4 | 前端框架 |
| Vue Router | 4.2 | 路由管理 |
| Pinia | 2.1 | 状态管理 |
| Element Plus | 2.5 | UI组件库 |
| Tailwind CSS | 3.4 | CSS框架 |
| ECharts | 5.4 | 图表库 |
| Axios | 1.6 | HTTP客户端 |

## 安全设计

### 1. 认证机制
- JWT Token认证
- Token过期时间：24小时
- 密码使用bcrypt加密

### 2. 权限控制
- 基于角色的访问控制（RBAC）
- ADMIN：管理员权限
- USER：普通用户权限

### 3. API安全
- AppKey/AppSecret双重验证
- 请求头验证
- CORS跨域配置

## 性能优化

### 1. 数据库优化
- 索引优化（username, app_key, date）
- 连接池管理
- 健康检查

### 2. 前端优化
- 路由懒加载
- 组件按需加载
- 静态资源CDN

### 3. 缓存策略
- 记忆文件本地缓存
- Token统计批量更新

## 扩展性设计

### 1. 水平扩展
- 无状态后端设计
- 数据库读写分离
- 负载均衡

### 2. 功能扩展
- 插件化LLM供应商
- 可配置记忆处理策略
- 自定义统计维度

### 3. 监控告警
- 日志收集
- 性能监控
- 异常告警

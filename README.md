# AI智能体营销平台

一个功能完整的AI智能体SaaS平台，支持多租户、推荐分组、双层记忆系统和Token统计分析。

## 核心特性

### 🎯 多租户架构
- AppKey/AppSecret认证机制
- 租户级别的API配置隔离
- 分组用户绑定管理

### 👥 推荐分组系统
- 用户注册时支持推荐人机制
- 自动创建和加入用户分组
- 分组内租户共享查看

### 🧠 双层记忆系统
- **KV事实记忆**：结构化信息提取（姓名、职业、偏好等）
- **行为摘要**：递归压缩的对话摘要
- **跨层引用检测**：自动识别历史对话引用
- **自动压缩**：超过3000字符时智能压缩

### 📊 Token统计分析
- 实时Token使用统计
- 月度对比分析（本月vs上月）
- 30天使用趋势可视化
- 请求次数追踪

### 🔧 灵活配置
- 数据库驱动的供应商配置
- 配置指南自动展示
- 支持多个AI供应商（OpenAI、通义千问等）

## 技术栈

### 后端
- FastAPI (Python 3.11)
- MySQL 8.0
- SQLAlchemy ORM
- JWT认证 + Bcrypt
- Snowflake ID生成

### 前端
- Vue 3
- Element Plus
- Tailwind CSS
- ECharts
- Axios

### 部署
- Docker
- Docker Compose
- Nginx

## 快速开始

### 前置要求

- Docker Desktop (Windows 11)
- 至少2GB可用内存
- 至少10GB可用磁盘空间

### 一键启动

1. 启动所有服务
```bash
docker-compose up -d --build
```

2. 等待服务启动（约1-2分钟）

3. 访问应用
- 前端地址：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 默认账号

- 管理员账号：`admin`
- 默认密码：`admin123`
- 访问：http://localhost/admin

## 项目结构

```
agent_marketing/
├── server/                 # 后端服务
│   ├── app/
│   │   ├── api/           # API路由
│   │   │   ├── admin/     # 管理员接口（用户、租户、供应商、Token、记忆）
│   │   │   ├── user/      # 用户接口（租户、统计）
│   │   │   └── proxy/     # AI中转接口
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   │   ├── memory_service.py    # 双层记忆系统
│   │   │   └── token_service.py     # Token统计
│   │   └── main.py        # 应用入口
│   ├── agent_config.json  # 系统配置
│   ├── memory_files/      # 记忆文件存储
│   ├── Dockerfile
│   └── requirements.txt
├── web/                    # 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   │   ├── admin/     # B端管理页面
│   │   │   └── user/      # C端用户页面
│   │   ├── router/        # 路由配置
│   │   └── api/           # API封装
│   ├── Dockerfile
│   └── package.json
├── init.sql               # 数据库初始化
├── docker-compose.yml     # Docker编排
├── DEPLOYMENT.md          # 详细部署文档
└── README.md
```

## 功能模块

### B端管理功能
- ✅ 用户管理（查看用户、推荐关系、分组）
- ✅ 租户管理（查看租户、绑定用户）
- ✅ 供应商管理（CRUD、配置指南）
- ✅ Token统计（总览、趋势图）
- ✅ 记忆查看（KV事实、行为摘要）

### C端用户功能
- ✅ 用户注册（推荐人机制）
- ✅ 租户管理（创建、分组绑定）
- ✅ API配置（供应商、Key、模型）
- ✅ 分组租户（查看同组租户）
- ✅ Token统计（个人使用、趋势）

## 核心功能说明

### 1. AI服务中转

通过统一的API接口调用多个AI供应商：

```bash
curl -X POST http://localhost:8000/api/proxy/chat/completions \
  -H "X-App-Key: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "model": "qwen-plus",
    "stream": false
  }'
```

### 2. 双层记忆系统

- **KV事实记忆**：自动提取结构化信息（姓名、职业、偏好语言、公司）
- **行为摘要**：每5-10轮对话生成摘要，超过3000字符递归压缩
- **跨层引用检测**：识别"之前"、"上次"等关键词
- **自动触发**：可配置触发阈值

存储格式：
```markdown
# KV事实记忆 (memory_kv_store_<AppKey>.md)
## 用户姓名
张三

## 职业
软件工程师

# 行为摘要 (memory_digest_<AppKey>.md)
[2026-04-03 10:30] 用户询问了Python编程相关问题...
[2026-04-03 10:35] 用户请求代码示例...
```

### 3. Token统计

- 实时统计每个租户的Token消耗
- 按日统计，支持30天趋势分析
- 月度对比（本月vs上月）
- 可视化图表展示（ECharts）

### 4. 推荐分组机制

- 用户注册时可填写推荐人ID
- 系统自动创建或加入推荐人的分组
- 分组内用户可查看所有租户
- 支持租户级别的用户绑定

## 数据库设计

### 核心表
- `tb_user` - 用户表（含phone, real_name, referral_id, group_id）
- `tb_tenant` - 租户表（含tenant_name, status, bound_users）
- `tb_provider` - 供应商表（含code, config_guide）
- `tb_provider_key` - API密钥表（改用app_key关联）
- `tb_conversation` - 对话记录表（新增）
- `tb_token_summary` - Token汇总表（含月度对比字段）
- `tb_token_daily` - Token日统计表（含request_count）
- `tb_memory_meta` - 记忆元数据表（含kv_file_path, digest_file_path）

## 配置说明

### 记忆系统配置

编辑 `server/agent_config.json`：

```json
{
  "database": {
    "url": "mysql+pymysql://root:password@mysql:3306/ai_agent_platform"
  },
  "memory_processing": {
    "rounds_threshold": 5,        // 每5轮触发记忆处理
    "enable_auto_processing": true,
    "digest_rounds": 10           // 每10轮生成摘要
  }
}
```

**重要**：LLM配置已从配置文件移除，改为通过管理页面配置到数据库。

### 环境变量

编辑 `docker-compose.yml`：

```yaml
environment:
  MYSQL_ROOT_PASSWORD: your-secure-password  # 修改MySQL密码
  SECRET_KEY: your-jwt-secret-key           # 修改JWT密钥
```

## 使用流程

### 管理员操作流程

1. 登录管理后台（/admin）
2. 在"供应商管理"中添加AI供应商
   - 填写名称、代码、Base URL
   - 填写配置指南（用户配置时显示）
3. 在"用户管理"中查看用户注册情况
4. 在"Token统计"中监控使用情况
5. 在"记忆查看"中查看租户记忆

### 用户操作流程

1. 注册账号（可填写推荐人手机号）
2. 登录后创建租户
   - 填写租户名称
   - 可选：绑定分组用户
3. 配置供应商API
   - 选择供应商
   - 查看配置指南
   - 填写API Key和模型
4. 使用AppKey调用API
5. 在"Token统计"中查看使用情况

## 开发指南

### 本地开发 - 后端

```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 本地开发 - 前端

```bash
cd web
npm install
npm run dev
```

## API文档

启动服务后访问：http://localhost:8000/docs

主要接口：

**认证**
- `POST /api/auth/register` - 用户注册（支持推荐人）
- `POST /api/auth/login` - 用户登录

**用户接口**
- `GET /api/user/profile` - 获取当前用户资料
- `PUT /api/user/profile` - 修改当前用户资料
- `POST /api/user/tenants` - 创建租户
- `GET /api/user/tenants` - 获取我的租户
- `GET /api/user/tenants/group` - 获取分组租户
- `GET /api/user/memory` - 获取当前用户租户记忆列表
- `GET /api/user/memory/{app_key}` - 获取当前用户指定租户记忆
- `POST /api/user/tenants/{app_key}/provider-keys` - 配置API Key
- `GET /api/user/token-stats` - 获取Token统计

**管理员接口**
- `GET /api/admin/users` - 用户列表
- `GET /api/admin/roles` - 角色权限列表
- `POST /api/admin/roles` - 新增角色
- `PUT /api/admin/roles/{role_code}` - 修改角色
- `DELETE /api/admin/roles/{role_code}` - 删除角色
- `PUT /api/admin/users/{user_id}/role` - 配置用户角色
- `GET /api/admin/groups` - 全部分组列表
- `GET /api/admin/tenants` - 租户列表
- `GET /api/admin/providers` - 供应商列表
- `GET /api/admin/token-stats` - Token统计
- `GET /api/admin/memory/{app_key}` - 查看记忆

**AI代理**
- `POST /api/proxy/chat/completions` - AI对话中转

## 常见问题

### 1. 数据库连接失败

确保MySQL容器已启动并健康：
```bash
docker-compose ps
docker-compose logs mysql
```

### 2. 前端无法访问后端

检查后端服务状态：
```bash
docker-compose logs backend
curl http://localhost:8000/
```

### 3. 记忆文件未生成

检查目录权限：
```bash
chmod 777 server/memory_files/
```

### 4. 重置数据库

```bash
docker-compose down -v
docker-compose up -d --build
```

## 部署文档

详细部署说明请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

包含：
- 完整部署步骤
- 配置说明
- 维护操作
- 性能优化
- 安全建议

## 安全建议

1. ⚠️ 修改默认管理员密码
2. ⚠️ 使用强密码作为JWT SECRET_KEY
3. ⚠️ 生产环境使用HTTPS
4. ⚠️ 定期备份数据库
5. ⚠️ 限制API访问频率
6. ⚠️ 定期更新依赖包

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-04-03)

首次发布，包含完整功能：
- ✅ 多租户架构
- ✅ 推荐分组系统
- ✅ 双层记忆系统（KV + Digest）
- ✅ Token月度对比统计
- ✅ 30天趋势可视化
- ✅ B端管理后台（用户、租户、供应商、Token、记忆）
- ✅ C端用户界面（注册、租户、API配置、统计）
- ✅ 对话记录追踪
- ✅ 跨层引用检测
- ✅ 数据库驱动的供应商配置

### v1.1.0 (2026-04-04)

- ✅ 角色权限管理（角色新增、修改、删除、用户角色分配）
- ✅ 管理员全局数据视图（用户、分组、租户、供应商、Token、记忆）
- ✅ 普通用户资料管理与个人记忆查看
- ✅ 顶部“用户”菜单，支持资料修改与退出
- ✅ 数据库角色表与用户角色编码升级

## 联系方式

如有问题，请提交Issue或查看详细文档。

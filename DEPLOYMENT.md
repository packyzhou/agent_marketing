# AI智能体平台 - 部署指南

## 系统概述

本系统是一个完整的AI智能体营销平台，包含以下核心功能：

### B端管理功能
- **用户管理**：查看所有用户信息、推荐关系、分组信息
- **租户管理**：管理所有租户、查看绑定用户
- **供应商管理**：配置AI模型供应商（OpenAI、通义千问等）
- **Token统计**：查看所有租户的Token使用情况和趋势
- **记忆查看**：查看租户的KV事实记忆和行为摘要记忆

### C端用户功能
- **用户注册**：支持推荐人机制，自动分组
- **租户管理**：创建租户、配置分组用户绑定
- **API配置**：为租户配置AI供应商API Key（带配置指南）
- **分组租户**：查看同组用户的所有租户
- **Token统计**：查看个人Token使用情况和30天趋势图

### 核心技术特性
- **双层记忆系统**：KV事实存储 + 行为摘要（递归压缩）
- **跨层引用检测**：自动识别用户对历史对话的引用
- **月度Token对比**：自动计算本月与上月Token使用变化
- **推荐分组机制**：基于推荐人自动创建和加入用户组
- **数据库驱动配置**：供应商API配置存储在数据库，非配置文件

## 技术栈

- **后端**：FastAPI + SQLAlchemy + MySQL
- **前端**：Vue3 + Element Plus + Tailwind CSS + ECharts
- **部署**：Docker + Docker Compose
- **认证**：JWT + Bcrypt
- **ID生成**：Snowflake算法

## 快速部署

### 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少10GB可用磁盘空间

### 2. 克隆项目（如适用）

```bash
cd /path/to/project
```

### 3. 配置环境变量

编辑 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  MYSQL_ROOT_PASSWORD: your-secure-password  # 修改MySQL密码
  SECRET_KEY: your-secret-key-change-in-production  # 修改JWT密钥
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 初始化数据

数据库会自动执行 `init.sql` 进行初始化，包括：
- 创建所有表结构
- 创建默认管理员账号（admin/admin123）

### 6. 访问系统

- **前端地址**：http://localhost
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs

### 7. 默认账号

- **管理员**：
  - 用户名：admin
  - 密码：admin123
  - 访问：http://localhost/admin

## 目录结构

```
.
├── server/                 # 后端服务
│   ├── app/
│   │   ├── api/           # API路由
│   │   │   ├── admin/     # 管理员API
│   │   │   ├── user/      # 用户API
│   │   │   └── proxy/     # AI代理API
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   │   ├── memory_service.py    # 双层记忆系统
│   │   │   └── token_service.py     # Token统计
│   │   └── core/          # 核心配置
│   ├── agent_config.json  # 系统配置
│   ├── memory_files/      # 记忆文件存储
│   └── Dockerfile
├── web/                   # 前端服务
│   ├── src/
│   │   ├── views/
│   │   │   ├── admin/     # B端管理页面
│   │   │   └── user/      # C端用户页面
│   │   ├── router/        # 路由配置
│   │   └── api/           # API请求
│   └── Dockerfile
├── init.sql              # 数据库初始化脚本
└── docker-compose.yml    # Docker编排配置
```

## 数据库表结构

### 核心表

1. **tb_user** - 用户表
   - 新增字段：phone, real_name
   - 支持推荐关系和分组

2. **tb_tenant** - 租户表
   - 新增字段：tenant_name, status, bound_users
   - 支持分组用户绑定

3. **tb_provider** - 供应商表
   - 新增字段：code, config_guide
   - 存储供应商配置指南

4. **tb_provider_key** - 供应商密钥表
   - 改用app_key关联租户
   - 新增model_name字段

5. **tb_conversation** - 对话记录表
   - 记录每轮对话内容
   - 用于记忆处理

6. **tb_token_summary** - Token汇总表
   - 新增：current_month_tokens, last_month_tokens
   - 支持月度对比

7. **tb_token_daily** - Token日统计表
   - 新增：request_count
   - 支持30天趋势分析

8. **tb_memory_meta** - 记忆元数据表
   - 新增：kv_file_path, digest_file_path
   - 支持双层记忆系统

## 配置说明

### agent_config.json

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

**注意**：LLM配置已从配置文件移除，改为通过管理页面配置到数据库。

## 使用流程

### 管理员操作流程

1. 登录管理后台（/admin）
2. 在"供应商管理"中添加AI供应商（如OpenAI、通义千问）
   - 填写供应商名称、代码、Base URL
   - 填写配置指南（用户配置时会显示）
3. 在"用户管理"中查看用户注册情况
4. 在"Token统计"中监控各租户使用情况
5. 在"记忆查看"中查看租户的记忆文件

### 用户操作流程

1. 注册账号（可填写推荐人ID）
2. 登录后创建租户
   - 填写租户名称
   - 可选：绑定分组用户
3. 配置供应商API
   - 选择供应商
   - 查看配置指南
   - 填写API Key和模型名称
4. 使用AppKey和AppSecret调用API
5. 在"Token统计"中查看使用情况

## API调用示例

### 调用AI对话接口

```bash
curl -X POST http://localhost:8000/api/proxy/chat/completions \
  -H "X-App-Key: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "model": "qwen-plus",
    "stream": false
  }'
```

### 响应格式

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "你好！有什么我可以帮助你的吗？"
      }
    }
  ],
  "usage": {
    "total_tokens": 25
  }
}
```

## 记忆系统说明

### KV事实记忆

自动提取结构化信息：
- 用户姓名
- 职业/职位
- 偏好语言
- 公司名称

存储格式：
```markdown
## 用户姓名
张三

## 职业
软件工程师

## 偏好语言
Python
```

### 行为摘要记忆

- 每5-10轮对话生成一次摘要
- 超过3000字符时递归压缩
- 保留最近5条记录，压缩旧记录
- 自动检测跨层引用（"之前"、"上次"等关键词）

## 常见问题

### 1. 容器启动失败

```bash
# 查看日志
docker-compose logs backend
docker-compose logs mysql

# 重启服务
docker-compose restart
```

### 2. 数据库连接失败

检查 `docker-compose.yml` 中的数据库配置是否正确。

### 3. 前端无法访问后端

确保后端服务已启动：
```bash
docker-compose ps
curl http://localhost:8000/
```

### 4. 记忆文件未生成

检查 `server/memory_files/` 目录权限：
```bash
chmod 777 server/memory_files/
```

## 维护操作

### 备份数据库

```bash
docker exec ai_agent_mysql mysqldump -uroot -prootpassword ai_agent_platform > backup.sql
```

### 恢复数据库

```bash
docker exec -i ai_agent_mysql mysql -uroot -prootpassword ai_agent_platform < backup.sql
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

## 性能优化建议

1. **数据库优化**
   - 定期清理旧的对话记录
   - 为常用查询字段添加索引

2. **记忆文件管理**
   - 定期归档旧的记忆文件
   - 监控磁盘使用情况

3. **Token统计**
   - 可考虑将日统计数据定期归档到月表

## 安全建议

1. 修改默认管理员密码
2. 使用强密码作为JWT SECRET_KEY
3. 在生产环境中使用HTTPS
4. 定期更新依赖包
5. 限制API访问频率
6. 定期备份数据库

## 技术支持

如遇问题，请检查：
1. Docker和Docker Compose版本
2. 端口占用情况（80, 8000, 3306）
3. 系统资源使用情况
4. 日志文件中的错误信息

## 更新日志

### v1.0.0 (2026-04-03)

- ✅ 完整的用户注册和推荐分组机制
- ✅ 租户管理和分组用户绑定
- ✅ 数据库驱动的供应商配置
- ✅ 双层记忆系统（KV + Digest）
- ✅ Token月度对比统计
- ✅ 30天使用趋势可视化
- ✅ B端管理后台（用户、租户、供应商、Token、记忆）
- ✅ C端用户界面（注册、租户、API配置、统计）
- ✅ 对话记录追踪
- ✅ 跨层引用检测

# AI智能体平台 - AI服务中转站 + 智能体能力复制平台

## 项目简介

本项目是一个完整的AI服务中转平台，提供以下核心功能：

- **AI服务中转**：统一接入多个AI供应商（阿里千问、字节豆包、Deepseek）
- **Token统计**：实时统计和分析Token消耗
- **双层记忆系统**：
  - 事实记忆（KV键值对）
  - 行为摘要（时间序列文本）
- **租户管理**：多租户隔离，支持AppKey/AppSecret认证
- **用户分组**：支持推荐人机制和分组管理
- **数据可视化**：30天Token消耗趋势图表

## 技术栈

### 后端
- FastAPI (Python 3.11)
- MySQL 8.0
- SQLAlchemy ORM
- JWT认证
- 异步处理

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
- Git

### 一键启动

1. 克隆项目
```bash
git clone <repository-url>
cd agent_marketing
```

2. 启动所有服务
```bash
docker-compose up -d
```

3. 等待服务启动（约1-2分钟）

4. 访问应用
- 前端地址：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 默认账号

- 管理员账号：`admin`
- 默认密码：`admin123`

## 项目结构

```
agent_marketing/
├── server/                 # 后端服务
│   ├── app/
│   │   ├── api/           # API路由
│   │   │   ├── admin/     # 管理员接口
│   │   │   ├── user/      # 用户接口
│   │   │   └── proxy/     # AI中转接口
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── web/                    # 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── api/           # API封装
│   ├── Dockerfile
│   └── package.json
├── init.sql               # 数据库初始化
├── docker-compose.yml     # Docker编排
└── README.md
```

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

- **事实记忆**：自动提取对话中的关键信息（姓名、电话等）
- **行为摘要**：记录用户行为的时间序列摘要
- **自动触发**：每5轮对话自动处理一次（可配置）

### 3. Token统计

- 实时统计每个租户的Token消耗
- 按日统计，支持30天趋势分析
- 可视化图表展示

## 配置说明

### 数据库配置

编辑 `server/agent_config.json`：

```json
{
  "database": {
    "host": "mysql",
    "port": 3306,
    "user": "root",
    "password": "rootpassword",
    "database": "ai_agent_platform"
  }
}
```

### 记忆处理配置

```json
{
  "memory_processing": {
    "rounds_threshold": 5,
    "enable_auto_processing": true
  }
}
```

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

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/user/tenants` - 创建租户
- `GET /api/user/stats/{app_key}` - 获取统计数据
- `POST /api/proxy/chat/completions` - AI对话中转

## 常见问题

### 1. 数据库连接失败

确保MySQL容器已启动并健康：
```bash
docker-compose ps
docker-compose logs mysql
```

### 2. 前端无法访问后端

检查Nginx配置和后端服务状态：
```bash
docker-compose logs frontend
docker-compose logs backend
```

### 3. 重置数据库

```bash
docker-compose down -v
docker-compose up -d
```

## 生产部署建议

1. 修改默认密码和密钥
2. 配置HTTPS证书
3. 启用数据库备份
4. 配置日志收集
5. 设置资源限制

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队。

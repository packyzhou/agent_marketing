# 🚀 快速启动指南

## 当前状态：✅ 已部署并运行

### 正在运行的服务
- ✅ MySQL数据库 (localhost:3306)
- ✅ 后端API (http://localhost:8000)

---

## 🎯 三种体验方式

### 方式1：可视化测试页面（推荐）
**最简单的方式，适合快速体验**

1. 双击打开文件：`test.html`
2. 点击页面上的按钮测试功能
3. 查看实时响应结果

### 方式2：API文档（推荐开发者）
**交互式API文档，可以直接测试所有接口**

浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 方式3：命令行测试
**适合自动化和脚本集成**

```bash
# 测试API连接
curl http://localhost:8000/

# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 🔑 默认账号

```
用户名: admin
密码: admin123
角色: ADMIN
```

---

## 📖 API使用示例

### 1. 用户登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

返回：
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### 2. 创建租户
```bash
curl -X POST http://localhost:8000/api/user/tenants \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"group_binding_json":""}'
```

### 3. 获取供应商列表
```bash
curl -X GET http://localhost:8000/api/admin/providers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🛠️ 管理命令

### 查看服务状态
```bash
cd d:\work\code\agent_marketing
docker-compose ps
```

### 查看日志
```bash
# 后端日志
docker logs ai_agent_backend

# MySQL日志
docker logs ai_agent_mysql

# 实时日志
docker-compose logs -f
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务
```bash
docker-compose down
```

### 重新启动
```bash
docker-compose up -d
```

---

## 📚 文档清单

| 文档 | 说明 |
|------|------|
| **DEPLOYMENT_STATUS.md** | 当前部署状态详情 |
| **README.md** | 项目介绍和功能说明 |
| **API_EXAMPLES.md** | 完整的API使用示例 |
| **ARCHITECTURE.md** | 系统架构设计 |
| **DEPLOY.md** | 详细部署指南 |
| **PROJECT_SUMMARY.md** | 项目完成总结 |

---

## 🎯 核心功能

### 已实现功能
✅ 用户认证（JWT）
✅ 租户管理
✅ 供应商管理
✅ AI服务中转
✅ Token统计
✅ 双层记忆系统
✅ 多租户隔离

### 预置数据
✅ 管理员账号（admin/admin123）
✅ 3个AI供应商（千问、豆包、Deepseek）
✅ 8张数据表
✅ 完整的API接口

---

## 🔍 故障排查

### 问题1：无法访问API
```bash
# 检查服务状态
docker-compose ps

# 查看后端日志
docker logs ai_agent_backend --tail 50

# 重启后端
docker-compose restart backend
```

### 问题2：数据库连接失败
```bash
# 检查MySQL状态
docker logs ai_agent_mysql

# 进入MySQL
docker exec -it ai_agent_mysql mysql -uroot -prootpassword
```

### 问题3：端口被占用
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 改为8001
```

---

## 📞 获取帮助

1. 查看API文档：http://localhost:8000/docs
2. 阅读项目文档（见上方文档清单）
3. 查看日志排查问题

---

## 🎊 项目亮点

- 🚀 Docker一键部署
- 📦 完整的Monorepo结构
- 🔐 JWT安全认证
- 💾 双层记忆系统
- 📊 Token统计可视化
- 📚 完善的API文档
- 🎯 多租户支持

---

**部署时间**: 2026-04-03
**状态**: ✅ 运行正常
**访问**: http://localhost:8000

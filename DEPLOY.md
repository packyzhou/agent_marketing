# 部署文档

## 系统要求

- Windows 11 Pro
- Docker Desktop 4.0+
- 至少4GB可用内存
- 至少10GB可用磁盘空间

## 部署步骤

### 方式一：使用启动脚本（推荐）

双击运行 `start.bat` 文件，脚本会自动：
1. 检查Docker环境
2. 构建并启动所有服务
3. 显示访问地址和默认账号

### 方式二：手动部署

1. 打开PowerShell或CMD
2. 进入项目目录
```bash
cd d:\work\code\agent_marketing
```

3. 启动服务
```bash
docker-compose up -d --build
```

4. 查看服务状态
```bash
docker-compose ps
```

## 服务说明

### MySQL数据库
- 端口：3306
- 用户：root
- 密码：rootpassword
- 数据库：ai_agent_platform

### 后端服务
- 端口：8000
- 框架：FastAPI
- 文档：http://localhost:8000/docs

### 前端服务
- 端口：80
- 框架：Vue 3 + Element Plus
- 访问：http://localhost

## 常用命令

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
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
# 停止所有服务
docker-compose down

# 停止并删除数据卷（重置数据库）
docker-compose down -v
```

### 更新代码后重新部署
```bash
docker-compose down
docker-compose up -d --build
```

## 数据持久化

- MySQL数据存储在Docker卷 `mysql_data` 中
- 记忆文件存储在 `./server/memory_files` 目录

## 故障排查

### 1. 端口被占用

如果80或8000端口被占用，修改 `docker-compose.yml`：

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # 改为8001
  frontend:
    ports:
      - "8080:80"    # 改为8080
```

### 2. MySQL初始化失败

查看MySQL日志：
```bash
docker-compose logs mysql
```

如需重新初始化：
```bash
docker-compose down -v
docker-compose up -d
```

### 3. 前端无法连接后端

检查Nginx配置和后端服务：
```bash
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
docker-compose exec backend curl http://localhost:8000
```

### 4. 内存不足

调整Docker Desktop内存限制：
- 打开Docker Desktop
- Settings -> Resources -> Memory
- 建议至少分配4GB

## 生产环境配置

### 1. 修改密钥

编辑 `docker-compose.yml`：
```yaml
backend:
  environment:
    SECRET_KEY: "your-production-secret-key-here"
```

### 2. 配置HTTPS

在 `web/nginx.conf` 中添加SSL配置：
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ...
}
```

### 3. 数据库备份

定期备份MySQL数据：
```bash
docker-compose exec mysql mysqldump -u root -prootpassword ai_agent_platform > backup.sql
```

### 4. 日志管理

配置日志轮转，避免日志文件过大：
```bash
docker-compose logs --tail=1000 > app.log
```

## 监控建议

1. 使用 `docker stats` 监控资源使用
2. 定期检查磁盘空间
3. 监控数据库连接数
4. 设置告警通知

## 安全建议

1. 修改所有默认密码
2. 限制数据库外部访问
3. 启用防火墙规则
4. 定期更新依赖包
5. 配置访问日志审计

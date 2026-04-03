# API使用示例

## 基础信息

- 基础URL：`http://localhost:8000/api`
- 认证方式：Bearer Token (JWT)
- 内容类型：`application/json`

## 1. 用户认证

### 1.1 用户注册

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "referral_id": null
  }'
```

响应：
```json
{
  "id": 1710000000000000001,
  "username": "testuser",
  "role": "USER",
  "group_id": null,
  "created_at": "2026-04-03T12:00:00"
}
```

### 1.2 用户登录

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 2. 租户管理

### 2.1 创建租户

```bash
curl -X POST http://localhost:8000/api/user/tenants \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_binding_json": ""
  }'
```

响应：
```json
{
  "app_key": "abc123def456...",
  "app_secret": "xyz789uvw012...",
  "user_id": 1710000000000000001,
  "group_binding_json": ""
}
```

### 2.2 获取租户列表

```bash
curl -X GET http://localhost:8000/api/user/tenants \
  -H "Authorization: Bearer YOUR_TOKEN"
```

响应：
```json
[
  {
    "app_key": "abc123def456...",
    "app_secret": "xyz789uvw012...",
    "user_id": 1710000000000000001,
    "group_binding_json": ""
  }
]
```

## 3. AI对话中转

### 3.1 发送对话请求（非流式）

```bash
curl -X POST http://localhost:8000/api/proxy/chat/completions \
  -H "X-App-Key: YOUR_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请介绍一下你自己"}
    ],
    "model": "qwen-plus",
    "stream": false
  }'
```

响应：
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "qwen-plus",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！我是一个AI助手..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### 3.2 发送对话请求（流式）

```bash
curl -X POST http://localhost:8000/api/proxy/chat/completions \
  -H "X-App-Key: YOUR_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "写一首诗"}
    ],
    "model": "qwen-plus",
    "stream": true
  }'
```

响应（Server-Sent Events）：
```
data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"春"}}]}

data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"风"}}]}

data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"拂"}}]}

data: [DONE]
```

## 4. 数据统计

### 4.1 获取Token统计

```bash
curl -X GET http://localhost:8000/api/user/stats/YOUR_APP_KEY \
  -H "Authorization: Bearer YOUR_TOKEN"
```

响应：
```json
{
  "daily": [
    {"date": "2026-03-04", "count": 1500},
    {"date": "2026-03-05", "count": 2300},
    {"date": "2026-03-06", "count": 1800}
  ],
  "total": 125000
}
```

## 5. 管理员接口

### 5.1 获取供应商列表

```bash
curl -X GET http://localhost:8000/api/admin/providers \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

响应：
```json
[
  {
    "id": 1,
    "name": "阿里千问",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "status": "ACTIVE"
  },
  {
    "id": 2,
    "name": "字节豆包",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "status": "ACTIVE"
  }
]
```

### 5.2 创建供应商

```bash
curl -X POST http://localhost:8000/api/admin/providers \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI",
    "base_url": "https://api.openai.com/v1"
  }'
```

## 6. Python SDK示例

```python
import requests

class AIAgentClient:
    def __init__(self, app_key, base_url="http://localhost:8000"):
        self.app_key = app_key
        self.base_url = base_url
    
    def chat(self, messages, model="qwen-plus", stream=False):
        url = f"{self.base_url}/api/proxy/chat/completions"
        headers = {
            "X-App-Key": self.app_key,
            "Content-Type": "application/json"
        }
        data = {
            "messages": messages,
            "model": model,
            "stream": stream
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()

# 使用示例
client = AIAgentClient(app_key="YOUR_APP_KEY")

messages = [
    {"role": "user", "content": "你好"}
]

result = client.chat(messages)
print(result["choices"][0]["message"]["content"])
```

## 7. JavaScript SDK示例

```javascript
class AIAgentClient {
  constructor(appKey, baseURL = 'http://localhost:8000') {
    this.appKey = appKey;
    this.baseURL = baseURL;
  }

  async chat(messages, model = 'qwen-plus', stream = false) {
    const response = await fetch(`${this.baseURL}/api/proxy/chat/completions`, {
      method: 'POST',
      headers: {
        'X-App-Key': this.appKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messages,
        model,
        stream
      })
    });

    return await response.json();
  }
}

// 使用示例
const client = new AIAgentClient('YOUR_APP_KEY');

const messages = [
  { role: 'user', content: '你好' }
];

client.chat(messages).then(result => {
  console.log(result.choices[0].message.content);
});
```

## 8. 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | 未授权 | 检查Token或AppKey是否正确 |
| 403 | 权限不足 | 检查用户角色权限 |
| 404 | 资源不存在 | 检查请求路径和参数 |
| 500 | 服务器错误 | 查看服务器日志 |

### 错误响应示例

```json
{
  "detail": "Invalid authentication credentials"
}
```

## 9. 最佳实践

### 9.1 Token管理
- 定期刷新Token
- 安全存储Token
- 不要在URL中传递Token

### 9.2 AppKey安全
- 不要在前端代码中硬编码AppKey
- 使用环境变量存储
- 定期轮换AppSecret

### 9.3 请求优化
- 使用连接池
- 实现请求重试机制
- 合理设置超时时间

### 9.4 记忆系统
- 每5轮对话自动处理记忆
- 记忆文件存储在服务器端
- 下次对话自动加载记忆

## 10. 测试工具

### Postman Collection

可以导入以下JSON到Postman进行测试：

```json
{
  "info": {
    "name": "AI Agent Platform",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\"username\":\"admin\",\"password\":\"admin123\"}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

## 11. 在线API文档

启动服务后，访问以下地址查看交互式API文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

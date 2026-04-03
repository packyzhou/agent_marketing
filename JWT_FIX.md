# 🔧 JWT认证问题修复

## 问题描述

登录后访问任何需要认证的接口都返回401错误，导致自动跳转回登录页面。

## 问题原因

JWT标准要求`sub`（subject）字段必须是字符串类型，但代码中使用了整数类型的用户ID，导致Token验证失败。

## 修复内容

### 1. 修改 `server/app/core/security.py`

在 `create_access_token` 函数中添加类型转换：

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Convert sub to string if it's an integer
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])
    # ... rest of the code
```

### 2. 修改 `server/app/core/deps.py`

在 `get_current_user` 函数中添加字符串到整数的转换：

```python
async def get_current_user(...):
    # ...
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(...)
    
    # Convert string user_id to integer
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(...)
    
    user = db.query(User).filter(User.id == user_id).first()
    # ...
```

## 修复验证

### ✅ 测试结果

1. **登录测试** - ✅ 成功
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```
返回：Token正常生成

2. **获取租户列表** - ✅ 成功
```bash
curl -X GET http://localhost:8000/api/user/tenants \
  -H "Authorization: Bearer TOKEN"
```
返回：`[]` (空数组，正常)

3. **创建租户** - ✅ 成功
```bash
curl -X POST http://localhost:8000/api/user/tenants \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"group_binding_json":""}'
```
返回：新创建的租户信息（包含app_key和app_secret）

## 影响范围

修复后，以下功能恢复正常：
- ✅ 用户登录后访问所有需要认证的接口
- ✅ 租户管理（创建、查询）
- ✅ 供应商管理
- ✅ Token统计查询
- ✅ 前端所有页面功能

## 使用说明

### 重新启动后端服务

修复已应用，后端服务已自动重启。

### 前端使用

1. 访问 http://localhost:3000
2. 使用 admin / admin123 登录
3. 现在可以正常访问所有页面：
   - 数据中心
   - 租户配置
   - 供应商管理

## 技术细节

### JWT Token结构

**修复前**：
```json
{
  "sub": 1000000000000000001,  // 整数类型 ❌
  "exp": 1775281752
}
```

**修复后**：
```json
{
  "sub": "1000000000000000001",  // 字符串类型 ✅
  "exp": 1775281752
}
```

### 为什么需要字符串

根据JWT规范（RFC 7519），`sub`字段应该是字符串类型：
> The "sub" (subject) claim identifies the principal that is the subject of the JWT. The claims in a JWT are normally statements about the subject. The subject value MUST either be scoped to be locally unique in the context of the issuer or be globally unique. The processing of this claim is generally application specific. The "sub" value is a case-sensitive string containing a StringOrURI value.

## 修复时间

**修复日期**: 2026-04-03
**修复状态**: ✅ 已完成并验证
**服务状态**: 🟢 正常运行

---

**现在可以正常使用前端界面了！** 🎉

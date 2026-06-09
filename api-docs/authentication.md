# 金蝶云星空旗舰版认证鉴权指南

## 认证方式

金蝶云星空旗舰版使用 **OAuth2 Accesstoken** 认证方式。

---

## 1. 获取 AccessToken

### 请求

```http
POST /kapi/oauth2/getToken
Content-Type: application/json
```

### 请求体

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "username": "your-username",
  "accountId": "your-account-id",
  "language": "zh_CN",
  "nonce": "a1b2c3d4e5f6",
  "timestamp": "2025-06-08 16:00:00"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `client_id` | String | ✅ | 应用 ID |
| `client_secret` | String | ✅ | AccessToken 认证密钥 |
| `username` | String | ✅ | 代理用户 |
| `accountId` | String | ✅ | 数据中心 ID |
| `language` | String | ❌ | 语言，默认 `zh_CN` |
| `nonce` | String | ✅ | 随机字符串（16-32 位） |
| `timestamp` | String | ✅ | 当前时间，格式 `YYYY-MM-DD HH:MM:SS` |

### 响应

```json
{
  "errorCode": "0",
  "data": {
    "access_token": "OPENAPIAUTH_xxx",
    "refresh_token": "xxx",
    "expires_in": 7200000
  },
  "status": true
}
```

---

## 2. 刷新 Token

### 请求

```http
POST /kapi/oauth2/refreshToken
Content-Type: application/json
```

### 请求体

```json
{
  "client_id": "your-client-id",
  "grant_type": "refresh_token",
  "refresh_token": "your-refresh-token",
  "accountId": "your-account-id",
  "nonce": "a1b2c3d4e5f6",
  "timestamp": "2025-06-08 16:00:00"
}
```

---

## 3. 使用 Token 调用 API

### 请求头

```http
Content-Type: application/json
accesstoken: {access_token}
x-acgw-identity: {x_acgw_identity}  # 可选
```

### 示例

```http
POST /kapi/v2/basedata/bd_material/query
Content-Type: application/json
accesstoken: OPENAPIAUTH_xxx
x-acgw-identity: djF8xxx

{
  "data": {
    "formId": "bd_material",
    "pageSize": 10,
    "pageNo": 1
  }
}
```

---

## 4. 错误码

| 错误码 | 说明 |
|--------|------|
| `0` | 成功 |
| `2501` | 不存在应用信息[网关] |
| `2551` | Token 无效或过期 |
| `401` | 未授权 |
| `403` | 禁止访问 |
| `400` | 请求参数错误 |
| `500` | 服务器内部错误 |

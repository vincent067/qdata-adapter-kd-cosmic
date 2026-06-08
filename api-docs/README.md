# 金蝶云星空旗舰版 API 文档

> 金蝶云星空旗舰版（kd-cosmic）OpenAPI 接口参考

## 文档来源

### 官方文档

- **金蝶开放平台**: https://open.kingdee.com/
- **API 文档中心**: [请填写具体文档 URL]
- **开发者社区**: [请填写社区 URL]

### 本目录文件说明

```
api-docs/
├── README.md                 # 本文档
├── apis_list.json           # 接口清单（从金蝶平台导出）
├── authentication.md        # 认证鉴权指南
├── scraped/                 # 爬取的官方文档
│   └── official-api-reference.md
└── examples/                # 官方请求示例
    └── sample-requests.md
```

---

## 认证方式

### OAuth2 Accesstoken 认证

| 参数 | 说明 | 必填 |
|------|------|------|
| `client_id` | 应用 ID（App ID） | ✅ |
| `client_secret` | AccessToken 认证密钥 | ✅ |
| `username` | 代理用户 | ✅ |
| `accountId` | 数据中心 ID | ✅ |
| `language` | 语言，默认 `zh_CN` | ❌ |
| `x_acgw_identity` | 第三方应用身份标识 | ❌ |

**获取 Token**:
```http
POST /kapi/oauth2/getToken
Content-Type: application/json

{
  "client_id": "your-client-id",
  "client_secret": "your-secret",
  "username": "your-username",
  "accountId": "your-account-id",
  "language": "zh_CN",
  "nonce": "随机字符串",
  "timestamp": "2025-01-01 12:00:00"
}
```

**请求头**:
```http
accesstoken: {access_token}
x-acgw-identity: {x_acgw_identity}
```

---

## 接口概览

### 基础数据（basedata）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/kapi/v2/basedata/bd_material/query` | 查询物料 |
| POST | `/kapi/v2/basedata/bd_material/save` | 保存物料 |
| POST | `/kapi/v2/basedata/bd_material/qeasyadd` | 快速新增物料 |

### 销售管理（sm）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/kapi/v2/null/sm/sm_salepricelist/qeasygetlist` | 查询销售价目表 |

### 标准 OpenAPI 格式

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/kapi/{app_id}/{form_id}/query` | 标准查询 |
| POST | `/kapi/{app_id}/{form_id}/save` | 标准保存 |

---

## 响应格式

### 成功响应

```json
{
  "errorCode": "0",
  "data": {
    "rows": [...],
    "header": [...],
    "count": 100,
    "page": 1,
    "pageSize": 10
  },
  "status": true
}
```

### 错误响应

```json
{
  "errorCode": "2501",
  "message": "不存在应用信息[网关]",
  "status": false
}
```

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2025-06 | 0.2.0 | 支持完全自定义 API 路径和方法 |
| 2025-05 | 0.1.0 | 初始版本，支持标准 OpenAPI 接口 |

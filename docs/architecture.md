# 适配器架构设计

## 整体架构

```
┌─────────────────────────────────────────┐
│           KdCosmicAdapter               │
│  (主适配器 - 组合器模式)                 │
├─────────────────────────────────────────┤
│  authenticate()   test_connection()     │
│  list_objects()   get_object()          │
│  create_object()  execute_custom_api()  │
│  raw_request()    invoke()              │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│   Standard    │       │  Enterprise   │
│  Interface    │       │  Interface    │
│  (standard)   │       │ (enterprise)  │
│   已实现       │       │   预留        │
└───────────────┘       └───────────────┘
```

## 接口模式

通过 `settings.interface` 参数动态选择接口实现：

```python
settings = {
    "interface": "standard",  # 默认，使用 OpenAPI Accesstoken 认证
    # "interface": "enterprise",  # 预留
}
```

## 路径构造规则

### 默认路径格式

```
/kapi/{app_id}/{form_id}/{operation}
```

示例：
- `/kapi/sys/bd_material/query`
- `/kapi/sys/bd_material/save`

### 带版本号

```
/kapi/v2/{app_id}/{form_id}/{operation}
```

示例：
- `/kapi/v2/null/sm/sm_salepricelist/qeasygetlist`

### 自定义路径

通过 `settings` 配置：

```python
settings = {
    "api_path_prefix": "/kapi/openapi",  # 自定义前缀
    "api_path_template": "{prefix}/{version}/{app_id}/{form_id}/{operation}",  # 自定义模板
}
```

## 认证流程

```
1. 调用 authenticate()
   └─> POST /kapi/oauth2/getToken
       └─> 获取 access_token

2. Token 应用到 HTTP Client
   └─> Header: accesstoken={token}
   └─> Header: x-acgw-identity={identity}

3. 后续请求自动携带 Token
   └─> 过期时自动刷新
```

## 自定义 API 调用方式

### 方式 1: execute_custom_api（推荐）

自动检查 `errorCode`，返回 `data` 字段。

```python
result = await adapter.execute_custom_api(
    path="/kapi/v2/basedata/bd_material/query",
    method="POST",
    body={"data": {"formId": "bd_material"}},
)
```

### 方式 2: invoke + 控制参数

通过 `params` 中的控制参数灵活调用。

```python
result = await adapter.invoke(
    "query",
    "bd_material",
    params={
        "_api_path": "/kapi/v2/basedata/bd_material/query",
        "_http_method": "POST",
        "_custom_body": True,
    },
    data={"data": {"formId": "bd_material"}},
)
```

### 方式 3: raw_request

完全透传，不做 `errorCode` 检查。

```python
result = await adapter.raw_request(
    path="/kapi/v2/basedata/bd_material/query",
    method="POST",
    body={"data": {}},
)
```

## 控制参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `_api_path` | 自定义 API 相对路径 | - |
| `_http_method` | HTTP 方法 | `POST` |
| `_custom_body` | `True` 时 data 直接作为请求体 | `False` |
| `_raw_response` | `True` 时返回原始响应 | `False` |

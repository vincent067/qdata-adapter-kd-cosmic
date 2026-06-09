# qdata-adapter-kd-cosmic 使用文档

> 金蝶云星瀚（Kingdee Cloud Cosmic / 轻易云）官方适配器

## 目录

- [概述](#概述)
- [安装](#安装)
- [认证配置](#认证配置)
- [核心方法](#核心方法)
- [操作类型详解](#操作类型详解)
- [使用示例](#使用示例)
- [错误处理](#错误处理)
- [版本历史](#版本历史)

---

## 概述

`qdata-adapter-kd-cosmic` 是 QDataV2 平台为 **金蝶云星瀚（Kingdee Cloud Cosmic）** 提供的官方适配器，支持通过标准接口调用金蝶 OpenAPI。

### 支持的平台

| 平台 | 适配器代码 | 说明 |
|------|-----------|------|
| 金蝶云星瀚 | `kd_cosmic` | 主适配器，支持标准接口 |

### 接口模式

- **standard**（标准接口）：支持 OAuth2 认证，覆盖查询、写入、自定义 API 调用

---

## 安装

```bash
pip install qdata-adapter-kd-cosmic
```

开发安装：

```bash
git clone <repo-url>
cd adapters/kd-cosmic
pip install -e ".[dev]"
```

---

## 认证配置

金蝶云星瀚采用 **OAuth2 Accesstoken** 认证模式，配置如下：

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `client_id` | ✅ | 应用客户端 ID |
| `client_secret` | ✅ | 应用客户端密钥 |
| `username` | ✅ | 登录用户名 |
| `accountId` | ✅ | 数据中心账号 ID |
| `x_acgw_identity` | ✅ | API 网关身份标识 |
| `language` | ❌ | 语言，默认 `zh_CN` |

### 认证流程

1. 调用 `POST /kapi/oauth2/getToken` 获取 accesstoken
2. 在后续请求头中携带 `accesstoken`
3. Token 过期时自动刷新（`POST /kapi/oauth2/refreshToken`）

---

## 核心方法

### 查询类

| 方法 | 说明 | 对应金蝶操作 |
|------|------|-------------|
| `list_objects(object_type, filters, page_size)` | 列表查询（自动翻页） | `query` / `qeasygetlist` |
| `get_object(object_type, object_id)` | 单条查询 | `query` |
| `query_objects(object_type, ...)` | 查询对象（生成器） | `query` |

### 写入类

| 方法 | 说明 | 对应金蝶操作 |
|------|------|-------------|
| `create_object(object_type, data, operation)` | 创建对象 | `save` / `qeasyadd` / 自定义 |

### 自定义 API

| 方法 | 说明 |
|------|------|
| `raw_request(path, method, body, headers)` | 原始 HTTP 请求，自动带认证头 |
| `execute_custom_api(path, method, body, headers)` | 自定义 API，自动检查 errorCode |

### 工具类

| 方法 | 说明 |
|------|------|
| `authenticate()` | 手动触发认证 |
| `refresh_token()` | 手动刷新 Token |
| `test_connection()` | 测试连接可用性 |
| `health_check()` | 健康检查 |

---

## 操作类型详解

### `create_object` 自定义操作类型

> **版本要求**: `>= 0.1.2`

金蝶云星瀚不同业务对象的"新增"接口可能使用不同的操作路径：

- 标准保存: `POST /kapi/{app_id}/{form_id}/save`
- 轻易云新增: `POST /kapi/v2/null/{app_id}/{form_id}/qeasyadd`

`create_object` 支持通过以下两种方式自定义操作类型：

#### 方式一：通过 `data._operation` 字段

```python
result = await adapter.create_object(
    "basedata.bd_material",
    {
        "number": "MAT001",
        "name": "测试物料",
        "_operation": "qeasyadd",  # 自定义操作类型
    }
)
```

**注意**: `_operation` 会从 `data` 中自动移除，不会发送到金蝶服务端。

#### 方式二：通过显式 `operation` 参数

```python
result = await adapter.create_object(
    "basedata.bd_material",
    {"number": "MAT001", "name": "测试物料"},
    operation="qeasyadd",  # 显式指定，优先级最高
)
```

**优先级**: `operation` 参数 > `data._operation` > 默认值 `"save"`

### `list_objects` 自定义操作类型

`list_objects` 同样支持自定义操作类型，通过 `filters._operation` 和 `filters._api_version`：

```python
async for record in adapter.list_objects(
    "sm.sm_salepricelist",
    filters={
        "_api_version": "v2/null",
        "_operation": "qeasygetlist",
    },
    page_size=10,
):
    print(record)
```

---

## 使用示例

### 示例 1：查询销售价目表

```python
from qdata_adapter_kd_cosmic import KdCosmicAdapter
from qdata_adapter import ConnectorContext

context = ConnectorContext(
    connector_id="my-connector",
    app_software_code="kd_cosmic",
    base_url="https://gzsz.test.kdgalaxy.com",
    auth_config={
        "client_id": "your-client-id",
        "client_secret": "your-secret",
        "username": "your-username",
        "accountId": "your-account-id",
        "x_acgw_identity": "your-identity",
    },
)

adapter = KdCosmicAdapter(context)

# 查询销售价目表
records = []
async for record in adapter.list_objects(
    "sm.sm_salepricelist",
    filters={"_api_version": "v2/null", "_operation": "qeasygetlist"},
    page_size=10,
):
    records.append(record)

print(f"共查询到 {len(records)} 条记录")
```

### 示例 2：物料新增（qeasyadd）

```python
# 轻易云物料新增接口
result = await adapter.create_object(
    "basedata.bd_material",
    {
        "number": "Item-00031996",
        "name": "测试物料001",
        "createorg_number": "00",
        "baseunit_number": "pcs",
        "group_number": "01",
        "modelnum": "规格型号1",
        "description": "描述1",
        "_operation": "qeasyadd",
    }
)

print(f"新增结果: {result}")
```

### 示例 3：自定义 API 调用

```python
# 调用金蝶自定义接口
result = await adapter.execute_custom_api(
    path="/kapi/v2/null/basedata/bd_material/qeasyadd",
    method="POST",
    body={
        "data": [
            {"number": "MAT001", "name": "测试物料"}
        ]
    },
)
```

---

## 错误处理

适配器将金蝶 API 错误统一转换为标准异常：

| 金蝶 errorCode | 适配器异常 | 说明 |
|----------------|-----------|------|
| `2501`, `2551`, `401`, `403` | `KdCosmicAdapterAuthError` | 认证失败 |
| 其他 | `KdCosmicAdapterAPIError` | API 调用失败 |
| 数据校验错误（4xx） | `ValidationError` | 请求数据不合法 |

### 响应格式

金蝶标准响应：
```json
{
  "errorCode": "0",
  "data": {...},
  "status": true
}
```

- `errorCode == "0"` 且 `status == true` 视为成功
- 失败时 `data` 中可能包含 `errorInfo` 数组，详细描述每条错误

---

## 版本历史

### [0.1.2] - 2026-06-09

- `create_object` 支持自定义操作类型（`_operation` 字段 / `operation` 参数）
- 新增 `create_object` 单元测试覆盖

### [0.1.1] - 2026-06-04

- 初始发布
- 支持 OAuth2 认证、查询、保存、自定义 API

### [0.1.0] - 2026-06-04

- 项目脚手架

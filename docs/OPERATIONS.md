# 金蝶云星瀚适配器 — 操作类型映射

> 本文档详细说明 `qdata-adapter-kd-cosmic` 中各方法对应的金蝶 OpenAPI 操作路径。

---

## 路径构建规则

金蝶 API 路径格式：

```
/kapi/{api_version}/{app_id}/{form_id}/{operation}
```

- `api_version`: 通过 `filters._api_version` 或 `settings.api_version` 指定，如 `v2/null`
- `app_id`: 从 `object_type` 解析（如 `basedata.bd_material` → `app_id=basedata`, `form_id=bd_material`）
- `operation`: 操作类型，如 `query`, `save`, `qeasyadd`, `qeasygetlist`

---

## 查询操作

### `list_objects` / `query_objects`

| 场景 | 默认操作 | 自定义方式 | 示例路径 |
|------|---------|-----------|---------|
| 标准查询 | `query` | — | `/kapi/basedata/bd_material/query` |
| 轻易云查询 | `qeasygetlist` | `filters._operation="qeasygetlist"` | `/kapi/v2/null/sm/sm_salepricelist/qeasygetlist` |

**请求体差异**:

- `query`: `{"data": {"formId": "...", "pageSize": 10, "pageNo": 1, ...}}`
- `qeasygetlist`: `{"data": {...}, "pageSize": 10, "pageNo": 1}`（pageSize 在顶层）

### `get_object`

始终使用 `query` 操作，通过 filter 限定单条记录。

---

## 写入操作

### `create_object`

| 场景 | 操作 | 触发方式 | 示例路径 |
|------|------|---------|---------|
| 标准保存 | `save` | 默认 | `/kapi/basedata/bd_material/save` |
| 轻易云新增 | `qeasyadd` | `data._operation="qeasyadd"` 或 `operation="qeasyadd"` | `/kapi/v2/null/basedata/bd_material/qeasyadd` |
| 其他自定义 | 任意 | `operation="xxx"` | `/kapi/{app_id}/{form_id}/xxx` |

**重要**: `data._operation` 会在发送请求前从 `data` 中移除，不会污染请求体。

### 轻易云新增请求体格式

参考 `apis_easycloud.json` 中的 `bd_material_qeasyadd`:

```json
{
  "data": [
    {
      "number": "Item-00031996",
      "name": "test001",
      "createorg_number": "00",
      "baseunit_number": "pcs",
      "group_number": "01",
      "modelnum": "规格型号1",
      "description": "描述1",
      "auxptyentry": [...],
      "entryentity": [...],
      "entry_groupstandard": [...]
    }
  ]
}
```

---

## 自定义 API

### `raw_request`

直接发送 HTTP 请求，**不检查 errorCode**，适用于需要自行处理响应的场景。

```python
response = await adapter.raw_request(
    path="/kapi/v2/null/basedata/bd_material/qeasyadd",
    method="POST",
    body={"data": [...]},
)
# 返回原始响应字典
```

### `execute_custom_api`

发送 HTTP 请求，**自动检查 errorCode**，失败时抛出异常。

```python
result = await adapter.execute_custom_api(
    path="/kapi/v2/null/basedata/bd_material/qeasyadd",
    method="POST",
    body={"data": [...]},
)
# 返回 response.data 字段
```

---

## 认证操作

| 方法 | 端点 | 说明 |
|------|------|------|
| `authenticate()` | `POST /kapi/oauth2/getToken` | 获取 accesstoken |
| `refresh_token()` | `POST /kapi/oauth2/refreshToken` | 刷新 accesstoken |

---

## 与 QDataV2 工作流节点映射

| 工作流节点 | 节点 operation | 适配器方法 | 适配器 operation |
|-----------|---------------|-----------|-----------------|
| `app_query` | — | `list_objects` / `query_objects` | `query` / `qeasygetlist` |
| `app_write` | `create` | `create_object` | `save` / `qeasyadd`（通过 `_operation` 透传） |
| `app_write` | `update` | `update_object` | `save` |
| `app_write` | `delete` | `delete_object` | `delete` |
| `app_write` | `upsert` | `update_object` / `create_object` | — |
| `app_write` | `action` | `execute_api` / `execute_action` | — |

---

## 快速参考

### 物料新增（轻易云）

```python
await adapter.create_object(
    "basedata.bd_material",
    {"number": "MAT001", "name": "测试物料", ...},
    operation="qeasyadd",
)
```

### 销售价目表查询（轻易云）

```python
async for r in adapter.list_objects(
    "sm.sm_salepricelist",
    filters={"_api_version": "v2/null", "_operation": "qeasygetlist"},
):
    print(r)
```

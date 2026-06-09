## 🎯 任务概述

请基于 QDataV2 适配器规范，开发 **kd-cosmic** 平台的官方适配器。

### 项目基本信息

- **适配器名称**: kd-cosmic
- **Python 包名**: qdata-adapter-kd-cosmic
- **主类名**: KdCosmicAdapter
- **模块名**: qdata_adapter_kd_cosmic
- 
- **接口模式**: 双接口
    - 主接口: `standard`
    - 备用接口: `enterprise`

---

## 📚 参考资源

### 官方文档

- **官方文档地址**: [请填写官方文档 URL]
- **API 参考**: [请填写 API 参考 URL]
- **开发者中心**: [请填写开发者中心 URL]

### 本地资源

```
项目根目录/
├── api-docs/                    # API 文档目录
│   ├── README.md               # 文档索引（请先阅读）
│   ├── openapi.yaml           # OpenAPI 定义（如有）
│   └── apis_list.json         # 接口清单（优先参考）
├── .env.example                # 环境变量模板（含两套环境配置）
├── .old-php/                   # 旧版 PHP 实现参考（仅作逻辑参考）
│   └── sdk/                    # PHP SDK 调用示例
├── src/qdata_adapter_kd_cosmic/    # 适配器源码目录
└── tests/                      # 测试目录
```

### 关键参考文件

1. **接口清单**: `api-docs/apis_list.json` - 完整的接口定义和参数
2. **环境配置**: `.env.example` - 包含沙箱/生产两套环境的测试配置
3. **PHP 参考**: `.old-php/sdk/` - 旧版调用逻辑参考（注意：仅参考逻辑，需按 Python 规范重写）

---

## 🏗️ 开发规范

### 1. 架构要求

基于 **qdata-adapter** SDK 开发：

```python
from qdata_adapter import BaseAppAdapter, ConnectorContext
from qdata_adapter.interfaces import StandardInterface, QimenInterface

class KdCosmicAdapter(BaseAppAdapter):
    """kd-cosmic 平台适配器"""

    # 平台标识
    app_software_code = "kd_cosmic"

    # 接口映射
    INTERFACE_MAP = {
        "standard": StandardInterface,
        "enterprise": QimenInterface,
    }
```

### 2. 目录结构

必须遵循以下结构：

```
src/qdata_adapter_kd_cosmic/
├── __init__.py           # 导出主类
├── adapter.py            # 主适配器实现
├── exceptions.py         # 自定义异常
├── auth.py               # 认证处理（如需要）
├── constants.py          # 常量定义
├── interfaces/           # 接口实现
│   ├── __init__.py
│   ├── base.py           # 接口基类
│   ├── standard.py    # 主接口
│
│   └── enterprise.py  # 备用接口
│
└── models/               # 数据模型（如需要）
    └── __init__.py
```

### 3. 接口规范

#### 双接口适配器要求

- 根据 `settings.interface` 参数动态选择接口实现
- 每个接口独立处理认证、请求、响应解析
- 接口间共享基础配置（base_url, auth_config）

#### 标准方法实现

必须实现以下核心方法：

```python
async def authenticate(self) -> AuthToken:
    """获取/刷新认证 Token"""

async def test_connection(self) -> ConnectionResult:
    """测试连接可用性"""

async def list_objects(
    self,
    object_type: str,
    filters: dict | None = None,
    page_size: int = 100
) -> AsyncIterator[dict]:
    """列表查询（自动分页）"""

async def get_object(self, object_type: str, object_id: str) -> dict:
    """单条查询"""
```

### 4. create_object 自定义操作类型（v0.1.2+）

金蝶不同业务对象的新增接口可能使用不同操作路径（如 `save`、`qeasyadd`）。`create_object` 必须支持自定义操作类型：

```python
async def create_object(
    self,
    object_type: str,
    data: dict[str, Any],
    operation: str | None = None,
) -> dict[str, Any]:
    """
    创建对象，支持自定义操作类型。

    优先级：operation 参数 > data._operation > 默认值 "save"
    """
    app_id, form_id = self._parse_object_type(object_type)
    op = operation if operation is not None else data.pop("_operation", "save")
    api_path = self._get_api_path(app_id, form_id, op)
    ...
```

**注意**:
- `_operation` 必须从 `data` 中 `pop` 移除，避免发送到服务端
- `operation` 参数优先级高于 `data._operation`
- 默认保持向后兼容，未指定时仍为 `"save"`
- 抽象基类 `BaseInterface.create_object` 签名必须同步更新

---

## 🧪 测试规范

### 测试原则

1. **只读测试**: 严禁新增、修改、删除数据，仅做查询类操作
2. **双环境验证**: 必须同时支持沙箱环境和生产环境
3. **Mock 优先**: 默认使用 Mock 数据，真实 API 测试需显式开启

### create_object 测试要求

必须覆盖以下场景：

```python
# 1. 默认 save 操作
await adapter.create_object("basedata.bd_material", {"number": "MAT001"})
# 预期路径: /kapi/basedata/bd_material/save

# 2. 通过 data._operation 自定义
await adapter.create_object("basedata.bd_material", {"number": "MAT001", "_operation": "qeasyadd"})
# 预期路径: /kapi/basedata/bd_material/qeasyadd
# 预期 data 中不包含 _operation

# 3. 通过 operation 参数自定义（最高优先级）
await adapter.create_object("basedata.bd_material", {"number": "MAT001", "_operation": "save"}, operation="qeasyadd")
# 预期路径: /kapi/basedata/bd_material/qeasyadd
```

### 测试环境配置

复制 `.env.example` 为 `.env`，填入两套环境的凭据：

```bash
# 沙箱环境
KD_COSMIC_BASE_URL=https://sandbox-api.example.com
KD_COSMIC_CLIENT_ID=sandbox-client-id
KD_COSMIC_CLIENT_SECRET=sandbox-secret

# 生产环境（谨慎使用）
# KD_COSMIC_BASE_URL=https://api.example.com
```

### 测试命令

```bash
# 运行所有测试（Mock 模式）
make test

# 沙箱环境真实 API 测试
USE_REAL_API=true KD_COSMIC_ENVIRONMENT=sandbox make test

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true make test
```

### 测试文件结构

```
tests/
├── __init__.py
├── conftest.py              # pytest 配置和 fixtures
├── test_adapter.py          # 主适配器测试
├── test_auth.py             # 认证测试
├── test_interfaces/         # 接口测试
│   ├── __init__.py
│   ├── test_standard.py
│
│   └── test_enterprise.py
│
└── data/                    # 测试数据
    ├── fixtures/            # 静态测试数据
    └── recordings/          # HTTP 录制（gitignore）
```

---

## 📝 开发步骤

### Phase 1: 分析设计（第 1 步）

1. 阅读 `api-docs/apis_list.json` 理解接口清单
2. 阅读 `.env.example` 了解认证方式和环境配置
3. 参考 `.old-php/sdk/` 理解旧版调用逻辑
4. 设计适配器架构：
    - 认证方式（OAuth2/API Key/HMAC/Session）
    - 接口划分（单接口/双接口）
    - 核心方法映射

### Phase 2: 核心实现（第 2-3 步）

1. **接口层实现**:
    - 实现 `interfaces/base.py` 定义接口基类
    - 实现 `interfaces/standard.py` 主接口
    - 实现 `interfaces/enterprise.py` 备用接口

2. **认证层实现**:
    - 根据 API 文档实现 Token 获取/刷新逻辑
    - 处理 Token 过期自动刷新

3. **适配器主类**:
    - 实现 `adapter.py` 主类
    - 实现标准方法（test_connection, list_objects, get_object）
    - 接口动态路由逻辑

### Phase 3: 测试验证（第 4 步）

1. 编写 Mock 测试用例
2. 配置 `.env` 进行沙箱环境测试
3. 验证所有查询类接口
4. 检查代码覆盖率（>80%）

### Phase 4: 文档完善（第 5 步）

1. 完善 `README.md` 使用示例
2. 更新 `api-docs/README.md` 接口说明
3. 编写 `examples/quickstart.py` 完整示例

---

## ⚠️ 重要约束

### 数据安全

- **严禁**: 在测试中创建、修改、删除任何数据
- **严禁**: 将真实凭据提交到 Git
- **必须**: 使用 `.env` 管理敏感配置
- **必须**: 检查 `.gitignore` 已包含 `.env` 和 `tests/data/recordings/`

### 代码质量

- 遵循 PEP8 规范
- 类型注解覆盖率 100%
- 核心方法必须有 docstring
- 使用 `ruff` 和 `black` 格式化代码：`make format`

### 兼容性

- Python 3.11+
- 支持 asyncio 异步调用
- 异常处理必须转换为 qdata-adapter 标准异常

### 向后兼容

- `create_object` 的 `operation` 参数必须为可选，默认 `None`
- 未传入 `operation` 且 `data` 中无 `_operation` 时，行为与旧版本一致（使用 `"save"`）

---

## 🔍 验收标准

完成开发后，必须满足：

- [ ] `make test` 所有测试通过（Mock 模式）
- [ ] `make check` 代码检查通过
- [ ] `make format` 格式化无变更
- [ ] 沙箱环境真实 API 测试通过
- [ ] 代码覆盖率 >= 80%
- [ ] `examples/quickstart.py` 可正常运行
- [ ] README 文档完整
- [ ] `create_object` 自定义操作类型有完整测试覆盖（默认 save / data._operation / 显式 operation）

---

## 💡 提示

### 从 PHP 迁移的注意事项

1. **数组 vs Dict**: PHP 数组对应 Python dict，注意嵌套结构
2. **JSON 处理**: Python 使用 `json.dumps()` / `json.loads()`
3. **异步调用**: 必须使用 `async/await`，不可使用同步 HTTP 库
4. **类型注解**: 添加完整的类型提示，特别是接口返回数据

### 常见问题

**Q: 如何处理分页？**
A: 在 `list_objects()` 中使用 `AsyncIterator`，内部自动处理翻页

**Q: Token 过期如何处理？**
A: 在 `authenticate()` 中实现刷新逻辑，配合 `is_token_expired()` 检查

**Q: 双接口如何切换？**
A: 通过 `context.settings["interface"]` 读取配置，在 `INTERFACE_MAP` 中映射

**Q: 如何支持金蝶轻易云的 `qeasyadd` 接口？**
A: 通过 `create_object` 的自定义操作类型：`data["_operation"] = "qeasyadd"` 或 `operation="qeasyadd"`

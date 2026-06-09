# 示例代码

此目录包含 kd-cosmic 适配器的使用示例。

## 文件说明

| 文件 | 说明 |
|------|------|
| `quickstart.py` | 快速开始示例，展示基础用法（认证、查询、自定义 API） |
| `custom_api_demo.py` | 自定义 API 调用示例（execute_custom_api / invoke / raw_request） |

## 运行示例

### 1. 配置环境变量

```bash
cp ../.env.example .env
# 编辑 .env 填入你的 API 凭据
```

### 2. 运行示例

```bash
# 快速开始
python quickstart.py

# 自定义 API 调用
python custom_api_demo.py
```

### 3. 使用真实 API（可选）

```bash
# 确保 .env 中配置了真实凭据
export USE_REAL_API=true
python quickstart.py
```

## 示例输出

```
============================================================
KdCosmicAdapter 快速开始示例
============================================================
🔗 连接到: https://gzsz.test.kdgalaxy.com
🆔 Client ID: qeasy...

📡 测试连接...
✅ 连接成功! (125ms)
   接口: standard

📋 标准查询示例
----------------------------------------
查询物料列表（前 3 条）:
  - Item-001: 测试物料
  - Item-002: 螺丝

🔧 自定义 API 调用示例
----------------------------------------

1. execute_custom_api - 直接调用任意 API
  成功! 返回数据字段数: 5
  记录数: 10

✨ 示例完成!
```

## 编写自己的代码

参考 `custom_api_demo.py` 创建你的应用：

```python
import asyncio
from qdata_adapter import ConnectorContext
from qdata_adapter_kd_cosmic import KdCosmicAdapter

async def my_app():
    context = ConnectorContext(
        connector_id="my-app",
        app_software_code="kd_cosmic",
        base_url="https://your-domain.kdgalaxy.com",
        auth_config={
            "client_id": "your-client-id",
            "client_secret": "your-secret",
            "username": "your-username",
            "accountId": "your-account-id",
        },
        settings={"interface": "standard"},
    )

    adapter = KdCosmicAdapter(context)

    # 自定义 API 调用
    result = await adapter.execute_custom_api(
        path="/kapi/v2/basedata/bd_material/query",
        method="POST",
        body={"data": {"formId": "bd_material"}},
    )
    print(result)

asyncio.run(my_app())
```

#!/usr/bin/env python3
"""
KdCosmicAdapter 快速开始示例

展示金蝶云星空旗舰版适配器的基础用法：
- 认证连接
- 标准查询（list_objects / get_object）
- 自定义 API 调用（execute_custom_api / invoke）

运行前请确保：
1. 已安装适配器: pip install -e .
2. 已配置环境变量 (cp .env.example .env 并填写)
"""

from __future__ import annotations

import asyncio
import os

from qdata_adapter import ConnectorContext
from qdata_adapter_kd_cosmic import KdCosmicAdapter


def load_env() -> dict[str, str]:
    """从环境变量加载配置"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    prefix = "KD_COSMIC"
    return {
        "base_url": os.getenv(f"{prefix}_BASE_URL", "https://api.example.com"),
        "client_id": os.getenv(f"{prefix}_CLIENT_ID", "your-client-id"),
        "client_secret": os.getenv(f"{prefix}_CLIENT_SECRET", "your-client-secret"),
        "username": os.getenv(f"{prefix}_USERNAME", "your-username"),
        "account_id": os.getenv(f"{prefix}_ACCOUNT_ID", "your-account-id"),
        "language": os.getenv(f"{prefix}_LANGUAGE", "zh_CN"),
        "x_acgw_identity": os.getenv(f"{prefix}_X_ACGW_IDENTITY", ""),
    }


async def demo_basic_query(adapter: KdCosmicAdapter) -> None:
    """标准查询示例"""
    print("\n📋 标准查询示例")
    print("-" * 40)

    # 查询物料列表（前 3 条）
    print("查询物料列表（前 3 条）:")
    count = 0
    async for item in adapter.list_objects("sys.bd_material", page_size=3):
        print(f"  - {item.get('number', 'N/A')}: {item.get('name', 'N/A')}")
        count += 1
    if count == 0:
        print("  （暂无数据）")


async def demo_custom_api(adapter: KdCosmicAdapter) -> None:
    """自定义 API 调用示例"""
    print("\n🔧 自定义 API 调用示例")
    print("-" * 40)

    # 示例 1: 使用 execute_custom_api 直接调用
    print("\n1. execute_custom_api - 直接调用任意 API")
    try:
        result = await adapter.execute_custom_api(
            path="/kapi/v2/basedata/bd_material/query",
            method="POST",
            body={
                "data": {
                    "formId": "bd_material",
                    "pageSize": 10,
                    "pageNo": 1,
                }
            },
        )
        rows = result.get("rows", [])
        print(f"  查询到 {len(rows)} 条物料记录")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例 2: 使用 invoke + 控制参数
    print("\n2. invoke + _api_path - 灵活调用")
    try:
        result = await adapter.invoke(
            "query",
            "bd_material",
            data={
                "data": {"formId": "bd_material"},
                "pageNo": 1,
                "pageSize": 10,
            },
            params={
                "_api_path": "/kapi/v2/basedata/bd_material/query",
                "_http_method": "POST",
                "_custom_body": True,
            },
        )
        print(f"  查询结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例 3: GET 请求示例
    print("\n3. GET 请求示例")
    try:
        result = await adapter.execute_custom_api(
            path="/kapi/v2/basedata/bd_material/list",
            method="GET",
            params={"pageSize": 10, "pageNo": 1},
        )
        print(f"  列表结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")


async def demo_raw_request(adapter: KdCosmicAdapter) -> None:
    """原始请求示例（不做 errorCode 检查）"""
    print("\n📡 原始请求示例（raw_request）")
    print("-" * 40)

    try:
        result = await adapter.raw_request(
            path="/kapi/v2/basedata/bd_material/query",
            method="POST",
            body={
                "data": {"formId": "bd_material"},
                "pageNo": 1,
                "pageSize": 10,
            },
        )
        print(f"  原始响应: {result}")
    except Exception as e:
        print(f"  错误: {e}")


async def main() -> None:
    """主函数"""
    config = load_env()

    print("=" * 60)
    print("KdCosmicAdapter 快速开始示例")
    print("=" * 60)
    print(f"🔗 连接到: {config['base_url']}")
    print(f"🆔 Client ID: {config['client_id'][:8]}...")

    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="quickstart-demo",
        app_software_code="kd_cosmic",
        base_url=config["base_url"],
        auth_config={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "username": config["username"],
            "accountId": config["account_id"],
            "language": config["language"],
            "x_acgw_identity": config["x_acgw_identity"],
        },
        settings={"interface": "standard"},
        environment="sandbox",
    )

    adapter = KdCosmicAdapter(context)

    try:
        # 1. 测试连接
        print("\n📡 测试连接...")
        result = await adapter.test_connection()
        if result.success:
            print(f"✅ 连接成功! ({result.duration_ms}ms)")
            print(f"   接口: {result.metadata.get('interface', 'unknown')}")
        else:
            print(f"❌ 连接失败: {result.message}")
            return

        # 2. 标准查询
        await demo_basic_query(adapter)

        # 3. 自定义 API
        await demo_custom_api(adapter)

        # 4. 原始请求
        await demo_raw_request(adapter)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 提示:")
        print("   1. 确保已配置正确的 API 凭据（.env 文件）")
        print("   2. 检查网络连接")
        print("   3. 查看 api-docs/ 了解 API 详情")
        raise

    print("\n" + "=" * 60)
    print("✨ 示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

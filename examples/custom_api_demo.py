#!/usr/bin/env python3
"""
KdCosmicAdapter 自定义 API 调用示例

展示如何通过 execute_custom_api / invoke / raw_request 灵活调用任意金蝶 API，
支持自定义路径、HTTP 方法、请求体和响应处理。
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


async def demo_execute_custom_api(adapter: KdCosmicAdapter) -> None:
    """execute_custom_api 示例 - 自动检查 errorCode"""
    print("\n🔧 execute_custom_api - 自动检查 errorCode")
    print("-" * 50)

    # 示例: 查询物料（POST）
    print("\n1. POST 查询物料")
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
        print(f"  成功! 返回数据字段数: {len(result)}")
        rows = result.get("rows", [])
        print(f"  记录数: {len(rows)}")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例: 列表查询（GET）
    print("\n2. GET 列表查询")
    try:
        result = await adapter.execute_custom_api(
            path="/kapi/v2/basedata/bd_material/list",
            method="GET",
            params={"pageSize": 10, "pageNo": 1},
        )
        print(f"  成功! 结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例: 保存操作（POST）
    print("\n3. POST 保存操作")
    try:
        result = await adapter.execute_custom_api(
            path="/kapi/v2/basedata/bd_material/save",
            method="POST",
            body={
                "data": {
                    "number": "Item-001",
                    "name": "测试物料",
                }
            },
        )
        print(f"  保存成功: {result}")
    except Exception as e:
        print(f"  错误: {e}")


async def demo_invoke(adapter: KdCosmicAdapter) -> None:
    """invoke 示例 - 通过控制参数灵活调用"""
    print("\n🎮 invoke - 通过控制参数灵活调用")
    print("-" * 50)

    # 示例 1: 使用 _api_path 指定完整路径
    print("\n1. _api_path - 指定完整路径")
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
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例 2: 使用 _raw_response 返回原始响应
    print("\n2. _raw_response - 返回原始响应（跳过 errorCode 检查）")
    try:
        result = await adapter.invoke(
            "query",
            "bd_material",
            data={"key": "value"},
            params={
                "_api_path": "/kapi/v2/basedata/bd_material/query",
                "_http_method": "POST",
                "_custom_body": True,
                "_raw_response": True,
            },
        )
        print(f"  原始响应: {result}")
    except Exception as e:
        print(f"  错误: {e}")

    # 示例 3: GET 请求
    print("\n3. GET 请求")
    try:
        result = await adapter.invoke(
            "query",
            "bd_material",
            params={
                "_api_path": "/kapi/v2/basedata/bd_material/list",
                "_http_method": "GET",
                "pageSize": 10,
                "pageNo": 1,
            },
        )
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")


async def demo_raw_request(adapter: KdCosmicAdapter) -> None:
    """raw_request 示例 - 完全透传，不做 errorCode 检查"""
    print("\n📡 raw_request - 完全透传，不做 errorCode 检查")
    print("-" * 50)

    # 示例: 原始 POST 请求
    print("\n1. 原始 POST 请求")
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

    # 示例: 带自定义 headers
    print("\n2. 带自定义 headers")
    try:
        result = await adapter.raw_request(
            path="/kapi/v2/basedata/bd_material/query",
            method="POST",
            body={"data": {}},
            headers={"X-Custom-Header": "custom-value"},
        )
        print(f"  原始响应: {result}")
    except Exception as e:
        print(f"  错误: {e}")


async def demo_salepricelist_query(adapter: KdCosmicAdapter) -> None:
    """销售价目表查询示例（真实接口）"""
    print("\n📋 销售价目表查询示例")
    print("-" * 50)

    try:
        result = await adapter.execute_custom_api(
            path="/kapi/v2/null/sm/sm_salepricelist/qeasygetlist",
            method="POST",
            body={
                "data": {},
                "pageNo": 1,
                "pageSize": 10,
            },
        )
        rows = result.get("rows", [])
        print(f"  查询到 {len(rows)} 条记录")
        for row in rows[:3]:
            print(f"    - {row.get('number', 'N/A')}: {row.get('name', 'N/A')}")
    except Exception as e:
        print(f"  错误: {e}")


async def main() -> None:
    """主函数"""
    config = load_env()

    print("=" * 60)
    print("KdCosmicAdapter 自定义 API 调用示例")
    print("=" * 60)
    print(f"🔗 连接到: {config['base_url']}")

    context = ConnectorContext(
        connector_id="custom-api-demo",
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
        # 认证
        print("\n📡 认证...")
        await adapter.authenticate()
        print("✅ 认证成功")

        # 演示各种调用方式
        await demo_execute_custom_api(adapter)
        await demo_invoke(adapter)
        await demo_raw_request(adapter)
        await demo_salepricelist_query(adapter)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        raise

    print("\n" + "=" * 60)
    print("✨ 示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

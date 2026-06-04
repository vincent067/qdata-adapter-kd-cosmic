"""
kd-cosmic enterprise 接口实现

备用接口实现，用于不同的 API 体系或认证方式。

开发者可根据实际平台需求：
1. 重命名此文件和类
2. 修改接口逻辑以适应不同的 API 规范
3. 调整认证方式（如 HMAC、签名等）
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import TYPE_CHECKING, Any, AsyncIterator

from qdata_adapter.exceptions import NotFoundError, ValidationError

from qdata_adapter_kd_cosmic.exceptions import KdCosmicAdapterAPIError, KdCosmicAdapterAuthError
from qdata_adapter_kd_cosmic.interfaces.base import BaseInterface

if TYPE_CHECKING:
    from qdata_adapter.client import HttpClient
    from qdata_adapter.context import ConnectorContext

logger = logging.getLogger(__name__)


class KdCosmicAdapterEnterpriseInterface(BaseInterface):
    """
    kd-cosmic enterprise 接口实现

    备用接口，支持不同的认证方式和 API 规范。
    可根据实际需求修改实现（如添加签名、使用不同的端点等）。

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="test",
        ...     app_software_code="kd_cosmic",
        ...     base_url="https://api-alt.example.com",
        ...     auth_config={
        ...         "app_key": "xxx",
        ...         "app_secret": "yyy",
        ...     },
        ... )
        >>> interface = KdCosmicAdapterEnterpriseInterface(context, http_client)
    """

    interface_name = "enterprise"

    def __init__(self, context: "ConnectorContext", http_client: "HttpClient") -> None:
        super().__init__(context, http_client)
        # 可根据需要配置不同的端点或参数
        self._api_endpoint = self.context.auth_config.get(
            "api_endpoint",
            f"{self.context.base_url}/gateway"
        )

    def _generate_signature(self, params: dict[str, Any]) -> str:
        """
        生成请求签名

        根据实际平台的签名规则实现。
        示例使用简单的 MD5 签名，实际应根据平台文档调整。

        Args:
            params: 请求参数

        Returns:
            签名字符串
        """
        auth_config = self.get_auth_config()
        app_secret = auth_config.get("app_secret", "")

        # TODO: 根据实际平台的签名规则实现
        # 示例：按参数名排序后拼接
        sorted_params = sorted(params.items())
        sign_str = app_secret + "".join(f"{k}{v}" for k, v in sorted_params) + app_secret
        return hashlib.md5(sign_str.encode()).hexdigest().upper()

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        根据此接口的认证方式实现（如签名、HMAC 等）

        Returns:
            认证信息

        Raises:
            KdCosmicAdapterAuthError: 认证失败
        """
        auth_config = self.get_auth_config()
        app_key = auth_config.get("app_key")
        app_secret = auth_config.get("app_secret")

        if not app_key or not app_secret:
            raise KdCosmicAdapterAuthError(
                "Missing app_key or app_secret",
                details={"missing": [k for k in ["app_key", "app_secret"] if not auth_config.get(k)]}
            )

        # TODO: 根据实际平台的认证方式实现
        # 某些接口可能不需要显式认证，而是在每个请求中携带签名
        return {
            "app_key": app_key,
            "authenticated": True,
        }

    async def list_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        列表查询（自动翻页）

        Args:
            object_type: 对象类型
            filters: 过滤条件
            page_size: 每页大小

        Yields:
            单条记录
        """
        filters = filters or {}
        page = 1
        has_more = True

        while has_more:
            # 构建请求参数
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            params = {
                "method": f"{object_type}.list",
                "app_key": self.get_auth_config().get("app_key"),
                "timestamp": timestamp,
                "page": page,
                "page_size": page_size,
                "biz_content": filters,
            }

            # 添加签名
            params["sign"] = self._generate_signature(params)

            try:
                # TODO: 根据实际 API 格式调整请求方式
                response = await self.http_client.post(
                    self._api_endpoint,
                    data=params,
                )

                # TODO: 根据实际响应格式调整
                result = response.get("response", {})
                items = result.get("data", [])

                for item in items:
                    yield item

                # 判断是否还有更多
                has_more = len(items) == page_size and result.get("has_more", False)
                page += 1

            except Exception as e:
                logger.error("Failed to fetch %s list: %s", object_type, e)
                raise KdCosmicAdapterAPIError(
                    f"Failed to list {object_type}",
                    details={"object_type": object_type, "page": page, "error": str(e)},
                ) from e

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """
        获取单个对象

        Args:
            object_type: 对象类型
            object_id: 对象 ID

        Returns:
            对象数据
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        params = {
            "method": f"{object_type}.get",
            "app_key": self.get_auth_config().get("app_key"),
            "timestamp": timestamp,
            "id": object_id,
        }
        params["sign"] = self._generate_signature(params)

        try:
            response = await self.http_client.post(
                self._api_endpoint,
                data=params,
            )
            result = response.get("response", {})
            return result.get("data", {})
        except Exception as e:
            if "404" in str(e) or "not exist" in str(e).lower():
                raise NotFoundError(
                    f"{object_type} not found",
                    resource_type=object_type,
                    resource_id=object_id,
                ) from e
            raise KdCosmicAdapterAPIError(
                f"Failed to get {object_type}",
                details={"object_type": object_type, "object_id": object_id},
            ) from e

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        创建对象

        Args:
            object_type: 对象类型
            data: 对象数据

        Returns:
            创建后的对象
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        params = {
            "method": f"{object_type}.create",
            "app_key": self.get_auth_config().get("app_key"),
            "timestamp": timestamp,
            "biz_content": data,
        }
        params["sign"] = self._generate_signature(params)

        try:
            response = await self.http_client.post(
                self._api_endpoint,
                data=params,
            )
            result = response.get("response", {})
            return result.get("data", {})
        except Exception as e:
            if "400" in str(e) or "invalid" in str(e).lower():
                raise ValidationError(
                    f"Invalid data for {object_type}",
                    details={"object_type": object_type, "data": data, "error": str(e)},
                ) from e
            raise KdCosmicAdapterAPIError(
                f"Failed to create {object_type}",
                details={"object_type": object_type},
            ) from e

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            True: 连接正常
            False: 连接异常
        """
        try:
            # 尝试调用一个简单的接口
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            params = {
                "method": "ping",
                "app_key": self.get_auth_config().get("app_key"),
                "timestamp": timestamp,
            }
            params["sign"] = self._generate_signature(params)

            await self.http_client.post(self._api_endpoint, data=params)
            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False


__all__ = ["KdCosmicAdapterEnterpriseInterface"]
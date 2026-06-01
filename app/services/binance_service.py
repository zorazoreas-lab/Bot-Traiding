import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from app.config import get_settings

settings = get_settings()


class BinanceAPIError(Exception):
    pass


class BinanceService:
    def __init__(self, api_key: str, secret_key: str, is_testnet: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = settings.binance_testnet_base_url if is_testnet else settings.binance_api_base_url

    def _headers(self) -> Dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key}

    def _signed_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(params or {})
        payload["timestamp"] = int(time.time() * 1000)
        payload.setdefault("recvWindow", 5000)
        # Binance change notice: percent-encode payload before computing HMAC signature.
        query_string = urlencode(payload, doseq=True)
        signature = hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        payload["signature"] = signature
        return payload

    async def _request(self, method: str, path: str, signed: bool = False, params: Optional[Dict[str, Any]] = None) -> Any:
        request_params = self._signed_params(params) if signed else (params or {})
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, f"{self.base_url}{path}", headers=self._headers(), params=request_params)
        if response.status_code >= 400:
            raise BinanceAPIError(f"Binance API error {response.status_code}: {response.text}")
        return response.json()

    async def ping(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/ping")

    async def account(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/account", signed=True)

    async def api_restrictions(self) -> Dict[str, Any]:
        # SAPI restrictions endpoint exists on production Binance. Testnet may not support it.
        if "testnet" in self.base_url:
            return {
                "enableReading": True,
                "enableSpotAndMarginTrading": True,
                "enableWithdrawals": False,
                "enableInternalTransfer": False,
                "ipRestrict": False,
                "note": "Testnet mode: restrictions endpoint may be unavailable, using safe simulated permissions after account validation."
            }
        return await self._request("GET", "/sapi/v1/account/apiRestrictions", signed=True)

    async def ticker_price(self, symbol: str) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/ticker/price", params={"symbol": symbol.upper()})

    async def avg_price(self, symbol: str) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/avgPrice", params={"symbol": symbol.upper()})

    async def klines(self, symbol: str, interval: str = "5m", limit: int = 30) -> Any:
        return await self._request("GET", "/api/v3/klines", params={"symbol": symbol.upper(), "interval": interval, "limit": limit})

    async def place_market_buy_quote(self, symbol: str, quote_order_qty: float) -> Dict[str, Any]:
        return await self._request(
            "POST",
            "/api/v3/order",
            signed=True,
            params={
                "symbol": symbol.upper(),
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": f"{quote_order_qty:.8f}",
            },
        )

    async def place_market_sell_qty(self, symbol: str, quantity: float) -> Dict[str, Any]:
        return await self._request(
            "POST",
            "/api/v3/order",
            signed=True,
            params={
                "symbol": symbol.upper(),
                "side": "SELL",
                "type": "MARKET",
                "quantity": f"{quantity:.8f}",
            },
        )

    async def cancel_open_orders(self, symbol: str) -> Any:
        return await self._request("DELETE", "/api/v3/openOrders", signed=True, params={"symbol": symbol.upper()})

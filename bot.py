from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Railway users normally set values from the Variables tab. Local users can use .env.
    This file intentionally accepts both older variable names from the first project
    and the clearer Railway names used in the deployment guide.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_name: str = "Binance Auto Aggressive Bot"
    app_env: str = "development"
    debug: bool = True
    base_url: str = "http://127.0.0.1:8000"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite:///./local.db"
    secret_key: str = Field(default="change_this_secret")
    encryption_key: str = Field(default="change_this_to_a_fernet_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"

    binance_use_testnet: bool = True
    # The service appends /api/v3 itself, so keep base URL without /api.
    binance_api_base_url: str = "https://api.binance.com"
    binance_live_base_url: str = "https://api.binance.com"
    binance_testnet_base_url: str = "https://testnet.binance.vision"
    binance_testnet_ws_url: str = "wss://stream.testnet.binance.vision/ws"
    binance_live_ws_url: str = "wss://stream.binance.com:9443/ws"
    enable_live_trading: bool = False
    paper_trading: bool = True

    bot_loop_interval_seconds: int = 15
    default_max_usable_percent: float = 10
    default_reserve_percent: float = 90
    max_allowed_usable_percent: float = 70
    default_stop_loss_percent: float = 2
    default_take_profit_percent: float = 3
    default_daily_loss_limit_percent: float = 3
    default_max_trade_per_day: int = 1
    default_cooldown_minutes: int = 360
    default_max_consecutive_losses: int = 3

    block_withdrawal_permission: bool = True
    spot_only: bool = True
    allow_futures: bool = False
    allow_margin: bool = False
    allow_withdrawal: bool = False

    frontend_url: str = "http://localhost:8000"
    allowed_origins: str = "*"
    # Backward compatibility with the first generated project.
    cors_origins: str = ""
    log_level: str = "INFO"

    @field_validator("binance_testnet_base_url", "binance_api_base_url", "binance_live_base_url")
    @classmethod
    def normalize_binance_base_url(cls, value: str) -> str:
        value = value.rstrip("/")
        # Users often paste the documented testnet REST root with /api. The code
        # already calls /api/v3/*, so remove trailing /api to avoid /api/api/v3.
        if value.endswith("/api"):
            value = value[:-4]
        return value

    @property
    def binance_base_url(self) -> str:
        return self.binance_testnet_base_url if self.binance_use_testnet else self.binance_live_base_url

    @property
    def cors_origin_list(self) -> List[str]:
        raw = self.allowed_origins or self.cors_origins or "*"
        if raw.strip() == "*":
            return ["*"]
        values = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
        frontend = (self.frontend_url or "").strip().rstrip("/")
        if frontend and frontend not in values:
            values.append(frontend)
        localhost_defaults = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        for origin in localhost_defaults:
            if self.app_env != "production" and origin not in values:
                values.append(origin)
        return values or ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

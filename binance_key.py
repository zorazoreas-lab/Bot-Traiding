from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings.

    The names map directly to Railway Variables / .env keys.  This class also
    keeps backward-compatible aliases such as ALLOWED_ORIGINS and
    BINANCE_LIVE_BASE_URL because older deployments used those names.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "Binance Auto Aggressive Bot"
    app_env: str = "development"
    debug: bool = True
    base_url: str = "http://127.0.0.1:8000"
    frontend_url: str = "http://127.0.0.1:8000"

    database_url: str = "sqlite:///./local.db"
    secret_key: str = Field(default="change_this_secret")
    encryption_key: str = Field(default="change_this_to_a_fernet_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"

    binance_use_testnet: bool = True
    binance_api_base_url: str = "https://api.binance.com"
    binance_live_base_url: str = "https://api.binance.com"
    binance_testnet_base_url: str = "https://testnet.binance.vision"
    binance_testnet_ws_url: str = "wss://stream.testnet.binance.vision/ws"
    binance_live_ws_url: str = "wss://stream.binance.com:9443/ws"
    enable_live_trading: bool = False
    paper_trading: bool = True

    # Optional: allow API key from Railway Variables for testnet deployments.
    # Safer default is database/web entry, but the user's requested workflow is supported.
    binance_api_key_source: str = "database"  # database | env
    binance_api_key: str = ""
    binance_secret_key: str = ""

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
    max_allowed_volatility_percent_5m: float = 3.0

    block_withdrawal_permission: bool = True
    spot_only: bool = True
    allow_futures: bool = False
    allow_margin: bool = False
    allow_withdrawal: bool = False

    # Both names are supported: CORS_ORIGINS and ALLOWED_ORIGINS.
    cors_origins: str = "*"
    allowed_origins: str = ""
    log_level: str = "INFO"

    @property
    def binance_base_url(self) -> str:
        return self.normalized_binance_testnet_base_url if self.binance_use_testnet else self.normalized_binance_live_base_url

    @property
    def normalized_binance_testnet_base_url(self) -> str:
        return self._normalize_binance_base(self.binance_testnet_base_url)

    @property
    def normalized_binance_live_base_url(self) -> str:
        return self._normalize_binance_base(self.binance_live_base_url or self.binance_api_base_url)

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.allowed_origins or self.cors_origins
        if raw.strip() == "*":
            return ["*"]
        values = [x.strip() for x in raw.split(",") if x.strip()]
        if self.frontend_url and self.frontend_url not in values:
            values.append(self.frontend_url)
        return values or ["*"]

    @staticmethod
    def _normalize_binance_base(value: str) -> str:
        """Allow both https://host and https://host/api in ENV.

        The service code calls /api/v3/... paths. If a user enters
        https://testnet.binance.vision/api, we remove the trailing /api to avoid
        https://testnet.binance.vision/api/api/v3/...
        """
        cleaned = (value or "").strip().rstrip("/")
        if cleaned.endswith("/api"):
            cleaned = cleaned[:-4]
        return cleaned


@lru_cache
def get_settings() -> Settings:
    return Settings()

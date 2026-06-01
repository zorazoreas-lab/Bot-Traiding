from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Binance Auto Aggressive Bot"
    app_env: str = "development"
    debug: bool = True
    base_url: str = "http://127.0.0.1:8000"

    database_url: str = "sqlite:///./local.db"
    secret_key: str = Field(default="change_this_secret")
    encryption_key: str = Field(default="change_this_to_a_fernet_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"

    binance_use_testnet: bool = True
    binance_api_base_url: str = "https://api.binance.com"
    binance_testnet_base_url: str = "https://testnet.binance.vision"
    enable_live_trading: bool = False

    bot_loop_interval_seconds: int = 15
    default_max_usable_percent: float = 50
    max_allowed_usable_percent: float = 70
    default_stop_loss_percent: float = 3
    default_take_profit_percent: float = 5
    default_daily_loss_limit_percent: float = 5
    default_max_trade_per_day: int = 3
    default_cooldown_minutes: int = 360
    cors_origins: str = "*"

    @property
    def binance_base_url(self) -> str:
        return self.binance_testnet_base_url if self.binance_use_testnet else self.binance_api_base_url


@lru_cache
def get_settings() -> Settings:
    return Settings()

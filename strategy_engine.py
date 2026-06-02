from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BinanceConnectRequest(BaseModel):
    api_key: str = Field(min_length=5)
    secret_key: str = Field(min_length=5)
    is_testnet: bool = True


class BotCreateRequest(BaseModel):
    bot_name: str = Field(min_length=2, max_length=120)
    symbol: str = "BTCUSDT"
    strategy_type: str = "TREND_BREAKOUT"
    paper_trading: bool = True
    max_usable_percent: float = 50
    stop_loss_percent: float = 3
    take_profit_percent: float = 5
    daily_loss_limit_percent: float = 5
    max_trade_per_day: int = 3
    cooldown_minutes: int = 360


class BotUpdateStatusRequest(BaseModel):
    status: str


class BotOut(BaseModel):
    id: int
    bot_name: str
    symbol: str
    strategy_type: str
    mode: str
    status: str
    paper_trading: bool
    max_usable_percent: float
    reserve_percent: float
    stop_loss_percent: float
    take_profit_percent: float
    daily_loss_limit_percent: float
    max_trade_per_day: int
    cooldown_minutes: int
    emergency_stop: bool

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    ok: bool
    message: str
    data: Optional[Any] = None

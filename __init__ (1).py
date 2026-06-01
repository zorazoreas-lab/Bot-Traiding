import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models import User
from app.routers import auth, binance, bots, trades
from app.services.bot_engine import bot_loop
from app.utils.security import get_password_hash

settings = get_settings()


def create_tables_and_admin():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.admin_email).first()
        if not existing:
            user = User(
                email=settings.admin_email,
                password_hash=get_password_hash(settings.admin_password),
                role="admin",
                status="active",
                is_active=True,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_and_admin()
    task = asyncio.create_task(bot_loop(SessionLocal))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = settings.cors_origin_list
allow_credentials = origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(binance.router)
app.include_router(bots.router)
app.include_router(trades.router)

static_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "app": settings.app_name,
        "env": settings.app_env,
        "live_trading_enabled": settings.enable_live_trading,
        "paper_trading_default": settings.paper_trading,
        "binance_testnet": settings.binance_use_testnet,
    }


@app.get("/api/frontend-config")
def frontend_config():
    return {
        "ok": True,
        "appName": settings.app_name,
        "env": settings.app_env,
        "testnet": settings.binance_use_testnet,
        "liveTradingEnabled": settings.enable_live_trading,
        "paperTradingDefault": settings.paper_trading,
    }


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")

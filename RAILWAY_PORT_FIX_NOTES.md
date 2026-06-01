# =========================================================
# APP CONFIG
# =========================================================
APP_NAME=Binance Auto Aggressive Bot
APP_ENV=production
DEBUG=false

# =========================================================
# SERVER / RAILWAY
# Do not set PORT manually in Railway. Railway injects PORT at runtime.
# start.py reads PORT safely and falls back to 8000 locally.
# =========================================================
HOST=0.0.0.0

# =========================================================
# DATABASE - Railway PostgreSQL or local SQLite
# Railway: DATABASE_URL=${{Postgres.DATABASE_URL}}
# Local:   DATABASE_URL=sqlite:///./local.db
# =========================================================
DATABASE_URL=${{Postgres.DATABASE_URL}}

# =========================================================
# ADMIN LOGIN
# =========================================================
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change_this_password

# =========================================================
# SECURITY
# SECRET_KEY: random long string.
# ENCRYPTION_KEY: Fernet key generated with:
# py -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# =========================================================
SECRET_KEY=change_this_to_a_very_long_random_secret_key_123456789_change_me
ENCRYPTION_KEY=PASTE_FERNET_KEY_HERE

# =========================================================
# BINANCE MODE - TESTNET FIRST
# =========================================================
BINANCE_USE_TESTNET=true
ENABLE_LIVE_TRADING=false
PAPER_TRADING=true

# =========================================================
# BINANCE API KEY FROM RAILWAY VARIABLES - TESTNET ONLY
# This project supports ENV key fallback via BINANCE_API_KEY_SOURCE=env.
# For production, prefer entering API key through the website/database.
# =========================================================
BINANCE_API_KEY_SOURCE=env
BINANCE_API_KEY=PASTE_TESTNET_API_KEY_HERE
BINANCE_SECRET_KEY=PASTE_TESTNET_SECRET_KEY_HERE

# =========================================================
# BINANCE URLS
# You can use with or without trailing /api; code normalizes it.
# =========================================================
BINANCE_TESTNET_BASE_URL=https://testnet.binance.vision/api
BINANCE_LIVE_BASE_URL=https://api.binance.com
BINANCE_API_BASE_URL=https://api.binance.com
BINANCE_TESTNET_WS_URL=wss://stream.testnet.binance.vision/ws
BINANCE_LIVE_WS_URL=wss://stream.binance.com:9443/ws

# =========================================================
# RAILWAY URL / CORS
# Replace URL-RAILWAY-ANDA with your Railway domain.
# Both ALLOWED_ORIGINS and CORS_ORIGINS are supported.
# =========================================================
FRONTEND_URL=https://URL-RAILWAY-ANDA.up.railway.app
ALLOWED_ORIGINS=https://URL-RAILWAY-ANDA.up.railway.app,http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000
CORS_ORIGINS=https://URL-RAILWAY-ANDA.up.railway.app,http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000

# =========================================================
# BOT DEFAULT SAFETY SETTINGS
# =========================================================
DEFAULT_MAX_USABLE_PERCENT=10
DEFAULT_RESERVE_PERCENT=90
DEFAULT_STOP_LOSS_PERCENT=2
DEFAULT_TAKE_PROFIT_PERCENT=3
DEFAULT_DAILY_LOSS_LIMIT_PERCENT=3
DEFAULT_MAX_TRADE_PER_DAY=1
DEFAULT_COOLDOWN_MINUTES=360
DEFAULT_MAX_CONSECUTIVE_LOSSES=3
MAX_ALLOWED_VOLATILITY_PERCENT_5M=3

# =========================================================
# TRADING SAFETY LOCK
# =========================================================
MAX_ALLOWED_USABLE_PERCENT=70
BLOCK_WITHDRAWAL_PERMISSION=true
SPOT_ONLY=true
ALLOW_FUTURES=false
ALLOW_MARGIN=false
ALLOW_WITHDRAWAL=false

# =========================================================
# LOGGING
# =========================================================
LOG_LEVEL=INFO

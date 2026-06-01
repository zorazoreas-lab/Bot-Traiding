# Binance Auto Aggressive Trading Bot Dashboard

A production-oriented FastAPI + PostgreSQL web dashboard for a Binance Spot trading bot using **Auto Aggressive Mode with Safety Lock**.

> Important: This project does not guarantee profit. It is designed to reduce operational risk with strict safety rules. Live trading is disabled by default.

## Core Features

- Admin login using JWT
- PostgreSQL database models
- Encrypted Binance API key storage
- Binance Spot API connection
- API permission checker
- Balance dashboard
- Live ticker price endpoint
- Bot creation page
- Auto Aggressive mode
- Safety locks:
  - Block bot if withdrawal permission is enabled
  - Block if trading permission is disabled
  - Reserve balance protection
  - Max usable balance limit, maximum 70%
  - Stop-loss required
  - Take-profit required
  - Daily loss limit
  - Max trades per day
  - Cooldown after loss
  - 3 consecutive losses = 24-hour pause
  - Emergency stop
- Paper trading by default
- Optional live trading only when `ENABLE_LIVE_TRADING=true`
- Trade history, order logs, and safety event logs
- Railway-ready configuration
- GitHub-ready project structure

## Recommended First Run

Use paper trading first. Do not use live mode until API keys, database, and safety settings are verified.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python scripts/create_admin.py
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Railway Deployment

1. Push this folder to GitHub.
2. Create a new Railway project.
3. Choose **Deploy from GitHub repo**.
4. Add a PostgreSQL service in Railway.
5. Railway will provide `DATABASE_URL`.
6. Add the variables from `.env.example` into Railway Variables.
7. Generate public domain under Railway Networking.

Railway can deploy FastAPI apps directly from GitHub. This project includes `railway.json`, `Procfile`, and `Dockerfile` options.

## Required Railway Variables

```text
APP_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=generate_a_long_random_secret
ENCRYPTION_KEY=generate_with_python_script_below
ADMIN_EMAIL=your_email@example.com
ADMIN_PASSWORD=change_this_password
ENABLE_LIVE_TRADING=false
BINANCE_USE_TESTNET=true
```

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Safety Defaults

```text
Spot only
Paper trading default
Max usable balance: 50%
Maximum allowed usable balance: 70%
Reserve balance: 50%
Stop loss: 3%
Take profit: 5%
Daily loss limit: 5%
Max trades per day: 3
Cooldown after loss: 6 hours
3 consecutive losses: pause 24 hours
```

## Live Trading Warning

Live orders are blocked unless:

```text
ENABLE_LIVE_TRADING=true
Bot paper_trading=false
API has trading permission
API withdrawal permission is disabled
Safety checks pass
```

Never enable withdrawal permission on a Binance API key used for this bot.

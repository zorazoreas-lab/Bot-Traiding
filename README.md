# Binance Auto Aggressive Bot with Safety Lock

This is a GitHub-ready and Railway-ready FastAPI web app for a Binance Spot Testnet trading bot dashboard.

The bot is designed for **Auto Aggressive Mode with Safety Lock**, not guaranteed profit. It starts in safe testing mode by default.

## Main features

- FastAPI backend
- Built-in HTML/CSS/JS frontend served from the same Railway domain
- PostgreSQL support for Railway
- SQLite support for local testing
- Binance Spot API integration
- Binance Spot Testnet support
- HMAC SHA256 Binance request signing
- Encrypted Binance API key storage
- Admin login with JWT token
- Auto Aggressive bot settings
- Max usable balance cap
- Reserve balance protection
- Stop loss and take profit requirement
- Daily loss limit
- Max trade per day
- Cooldown after loss
- Consecutive loss cooldown
- Emergency stop
- Trade logs
- Safety event logs
- Paper trading default
- Live trading disabled by default

## Important safety note

This project does not guarantee profit. Trading always has risk. Start with Binance Spot Testnet and paper trading first.

Default safe mode:

```env
BINANCE_USE_TESTNET=true
ENABLE_LIVE_TRADING=false
PAPER_TRADING=true
```

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# paste the generated key into ENCRYPTION_KEY in .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Railway deploy

See:

```text
GITHUB_RAILWAY_DEPLOY_STEPS.md
```

## Environment variables

Use `.env.example` as the full template.

For Railway, replace:

```env
FRONTEND_URL=https://URL-RAILWAY-ANDA.up.railway.app
ALLOWED_ORIGINS=https://URL-RAILWAY-ANDA.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## Binance Testnet API key

Create HMAC-SHA-256 API key from Binance Spot Testnet. Put the API key and secret key through the website page, not directly in code.

## Recommended first bot setting

```text
Pair: BTCUSDT
Paper Trading: true
Max Usable Balance: 10%
Reserve Balance: 90%
Stop Loss: 2%
Take Profit: 3%
Daily Loss Limit: 3%
Max Trade Per Day: 1
Cooldown: 360 minutes
```

## File structure

```text
app/
  config.py
  database.py
  main.py
  models/
  routers/
  services/
  utils/
frontend/
  index.html
  styles.css
  app.js
requirements.txt
Dockerfile
Procfile
railway.json
.env.example
GITHUB_RAILWAY_DEPLOY_STEPS.md
```


## Railway start command fix

This version uses `start.py` as the production entry point. Railway injects a `PORT` environment variable at runtime. Do not create your own `PORT` variable in Railway Variables.

Required start command:

```bash
python start.py
```

Files updated for Railway:

- `start.py`
- `Procfile`
- `railway.json`
- `Dockerfile`

If Railway still shows `Invalid value for --port: ${PORT}`, check Railway service settings and remove any old custom Start Command that contains `${PORT}`.

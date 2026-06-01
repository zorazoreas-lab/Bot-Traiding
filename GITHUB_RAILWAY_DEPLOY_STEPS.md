# GitHub + Railway Deployment Steps

## A. Push to GitHub

```bash
git init
git add .
git commit -m "Initial Binance safety trading bot dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## B. Deploy to Railway from GitHub

1. Open Railway.
2. New Project.
3. Deploy from GitHub repo.
4. Choose this repo.
5. Add PostgreSQL plugin/service.
6. Go to the web service Variables.
7. Add variables from `.env.example`.
8. Set:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
ENABLE_LIVE_TRADING=false
BINANCE_USE_TESTNET=true
```

9. Deploy.
10. Open Settings → Networking → Generate Domain.

## C. Production Checklist

- `SECRET_KEY` must be long and random.
- `ENCRYPTION_KEY` must be generated using Fernet.
- `ADMIN_PASSWORD` must be changed.
- `ENABLE_LIVE_TRADING` should stay `false` until all paper tests pass.
- Binance API must have withdrawal permission OFF.
- Prefer Binance API IP restriction if you use a stable server IP.

## D. First Test

1. Login with admin credentials.
2. Connect Binance Testnet API key.
3. Create Paper Bot.
4. Click Run Once.
5. Check Logs and Safety Events.
6. Only after repeated tests, consider live mode.

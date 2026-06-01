# Test Report

## Latest version: v3 Railway Port Fix

Checks performed after the Railway port fix:

```text
python -m compileall -q . : PASS
pytest -q : 4 passed
```

## Fixed deployment issue

The previous Railway logs showed:

```text
Error: Invalid value for '--port': '${PORT}' is not a valid integer.
```

This version avoids direct shell expansion in Railway start commands by using `start.py`:

```python
port = int(os.environ.get("PORT", "8000"))
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

## Important Railway note

Do not manually create a `PORT` variable in Railway Variables. Railway injects it automatically.


--- Previous report ---

# Test Report

## Changes in this version

- Added Railway URL environment support using `FRONTEND_URL` and `ALLOWED_ORIGINS`.
- Kept backward compatibility with `cors_origins`.
- Fixed Binance Testnet base URL normalization so both `https://testnet.binance.vision/api` and `https://testnet.binance.vision` work.
- Added `/api/frontend-config` endpoint.
- Improved frontend API client so same-domain Railway deploy works without hardcoded localhost.
- Added `tests/conftest.py` so tests can import the app reliably.
- Added `bcrypt==3.2.2` pin to avoid Passlib/bcrypt compatibility issue on newer Python environments.
- Kept all existing bot, safety lock, Binance, dashboard, order, log, and emergency stop functions.

## Test executed

```bash
python -m compileall app
pytest -q
```

Result:

```text
compileall: PASS
pytest: 4 passed
```

Warnings from dependencies/date handling appeared, but no test failed.

## Manual website test checklist

1. Start app.
2. Open `/`.
3. Login using `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
4. Open `/api/health`.
5. Connect Binance Spot Testnet API key.
6. Run permission check.
7. Load balance.
8. Create bot with paper trading enabled.
9. Click Run Once.
10. Check trade logs and safety logs.
11. Press Emergency Stop.

## Safe environment for first Railway test

```env
BINANCE_USE_TESTNET=true
ENABLE_LIVE_TRADING=false
PAPER_TRADING=true
```

## v4 Railway Nixpacks Build Fix
- Removed active Dockerfile to avoid Dockerfile parser error.
- Forced Railway builder to NIXPACKS in railway.json.
- Kept Procfile as `web: python start.py`.
- Confirmed project compiles without syntax errors.

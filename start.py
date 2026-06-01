# GitHub + Railway Deploy Steps

1. Upload this cleaned project folder to a GitHub repository.
2. In Railway, create a new project from the GitHub repo.
3. Add PostgreSQL service if you want PostgreSQL.
4. In the web/backend service, add Variables from `.env.example`.
5. Replace `FRONTEND_URL`, `ALLOWED_ORIGINS`, `CORS_ORIGINS`, `ENCRYPTION_KEY`, `SECRET_KEY`, admin login, and Binance testnet API key values.
6. Do not add a manual `PORT` variable.
7. Redeploy.

Expected Railway start command:

```text
python start.py
```

Expected `Procfile`:

```text
web: python start.py
```

Expected `railway.json`:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "python start.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

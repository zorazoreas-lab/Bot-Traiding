# Railway Port Fix Notes

This version fixes the Railway crash:

```text
Error: Invalid value for '--port': '${PORT}' is not a valid integer.
```

## What changed

- Added `start.py` as the only production start entry point.
- Updated `Procfile` to:

```text
web: python start.py
```

- Updated `railway.json` to:

```json
{
  "deploy": {
    "startCommand": "python start.py"
  }
}
```

- Updated `Dockerfile` to:

```Dockerfile
CMD ["python", "start.py"]
```

## Railway Variables

Do not create a manual `PORT` variable in Railway. Railway injects `PORT` automatically.

If you previously added any of these, delete them:

```env
PORT=${PORT}
PORT=8000
```

## After pushing to GitHub

1. Push this full project to GitHub.
2. Go to Railway.
3. Open the service settings.
4. Make sure there is no old custom start command containing `${PORT}`.
5. Redeploy.

## Test result

Local checks completed:

```text
python -m compileall -q . : PASS
pytest -q : 4 passed
```

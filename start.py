"""Railway/production entry point.

This file avoids shell-specific PORT expansion issues such as Railway reading
"${PORT}" as a literal string. Railway injects PORT at runtime; locally we
fall back to 8000.
"""

from __future__ import annotations

import os
import sys

import uvicorn


def get_port() -> int:
    raw_port = os.environ.get("PORT", "8000").strip()
    try:
        return int(raw_port)
    except (TypeError, ValueError):
        print(
            f"Invalid PORT value {raw_port!r}; falling back to 8000.",
            file=sys.stderr,
        )
        return 8000


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=get_port(),
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )

from __future__ import annotations

import uvicorn

from .api import app


def run() -> None:
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()

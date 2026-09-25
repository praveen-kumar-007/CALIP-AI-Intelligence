import sys
import traceback
from pathlib import Path

# Ensure CALIP project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from app.main import app as fastapi_app
except Exception:
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse

    fastapi_app = FastAPI()

    @fastapi_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def error_route(path: str):
        return PlainTextResponse(f"Startup Exception in CALIP:\n\n{err_tb}", status_code=500)

# Vercel Serverless Function entry point
app = fastapi_app


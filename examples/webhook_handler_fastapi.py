"""Example FastAPI webhook handler for serviceApp events."""

import os
from typing import Any

from fastapi import FastAPI, Request

from webex_byova import BYOVA

app = FastAPI()
sdk = BYOVA.from_env()


@app.post("/webhooks/webex")
async def webex_webhook(request: Request) -> dict[str, Any]:
    payload = await request.json()
    result = await sdk.ahandle_service_app_webhook(payload)
    return {"status": "ok", "org_id": result.org_id, "event": result.event}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

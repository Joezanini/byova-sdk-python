"""Example: Integration OAuth + webhook registration."""

import asyncio
import os

from webex_byova import BYOVA


async def main() -> None:
    sdk = BYOVA.from_env()

    print("Opening browser for Integration OAuth (developer authorization)...")
    await sdk.integration.aauthorize(open_browser=True)
    print("Integration authorized.")
    print("Access token:", sdk.integration.access_token)
    print("Refresh token:", sdk.integration.refresh_token)
    print("Expires at:", sdk.integration.expires_at)
    print("Scopes:", sdk.integration.scopes)
    

    target = os.environ.get("WEBEX_WEBHOOK_TARGET_URL")
    if target:
        created = await sdk.webhooks.aensure_service_app_webhooks(target)
        print(f"Registered {len(created)} webhook(s) -> {target}")
    else:
        print("Set WEBEX_WEBHOOK_TARGET_URL to register serviceApp webhooks.")

    await sdk.aclose()


if __name__ == "__main__":
    asyncio.run(main())

"""Example: Integration OAuth + webhook registration."""

import asyncio
import os

from webex_byova import BYOVA


async def main() -> None:
    sdk = BYOVA.from_env()

    print("Opening browser for Integration OAuth (developer authorization)...")
    await sdk.integration.aauthorize(
        scopes=[
            "spark:applications_token",
            "application:webhooks_write",
            "application:webhooks_read",
        ],
        open_browser=True,
    )
    print("Integration authorized.")

    target = os.environ.get("WEBEX_WEBHOOK_TARGET_URL")
    if target:
        created = await sdk.webhooks.aensure_service_app_webhooks(target)
        print(f"Registered {len(created)} webhook(s) -> {target}")
    else:
        print("Set WEBEX_WEBHOOK_TARGET_URL to register serviceApp webhooks.")

    await sdk.aclose()


if __name__ == "__main__":
    asyncio.run(main())

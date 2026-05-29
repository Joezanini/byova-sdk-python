"""Example: manual Service App refresh token (sandbox)."""

import asyncio
import os

from webex_byova import BYOVA


async def main() -> None:
    sdk = BYOVA.from_env()
    org_id = os.environ["WEBEX_ORG_ID"]
    refresh_token = os.environ["WEBEX_SA_REFRESH_TOKEN"]

    await sdk.service_app.asave_registration(org_id, refresh_token)
    client = await sdk.aget_client_for_org(org_id)
    schemas = await client.schemas.alist()
    print(f"Found {len(schemas)} schema(s)")
    await sdk.aclose()


if __name__ == "__main__":
    asyncio.run(main())

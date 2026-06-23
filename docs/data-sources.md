# Data Sources

For where data source registration fits in the overall BYOVA workflow, see the [BYOVA Data Journey](concepts/data-journey.md#phase-3).

## CRUD operations

```python
client = await sdk.aget_client_for_org(org_id)

# List
items = await client.data_sources.alist()

# Create
from webex_byova.models import DataSourceCreate
ds = await client.data_sources.acreate(DataSourceCreate(
    audience="MyApp",
    subject="callAudioData",
    nonce="unique-nonce",
    schema_id="78efc775-dccb-45ca-9acf-989a4a59f788",
    url="https://dap.example.com/ingest",
    token_lifetime_minutes=60,
))

# Get / Update / Delete
detail = await client.data_sources.aget(ds.id)
await client.data_sources.aupdate(ds.id, {"status": "disabled", "errorMessage": "maintenance"})
await client.data_sources.adelete(ds.id)
```

Schema discovery is covered in [Schemas](guides/schemas.md).

## Token extension

Update with a new `nonce` and `tokenLifetimeMinutes` before the JWS token expires (max 1440 minutes).

## Scopes

- Read: `spark-admin:datasource_read`
- Write: `spark-admin:datasource_write`

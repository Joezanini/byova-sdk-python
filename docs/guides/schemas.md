# Schemas

Before creating a data source, discover available BYODS schemas for the organization.

## List schemas

```python
client = await sdk.aget_client_for_org(org_id)
schemas = await client.schemas.alist()

for schema in schemas:
    print(schema.id, schema.service_type, schema.protocol)
```

## Get schema details

```python
schema = await client.schemas.aget(schema_id)
print(schema.app_type, schema.url)
```

## Workflow

1. Customer admin authorizes your Service App (webhook or sandbox registration)
2. Obtain an `OrgClient` via `aget_client_for_org(org_id)`
3. List schemas to find the correct `schemaId`
4. Create a data source with that schema — see [Data Sources](../data-sources.md)

```python
schemas = await client.schemas.alist()
schema_id = schemas[0].id

await client.data_sources.acreate({
    "audience": "MyVirtualAgent",
    "subject": "callAudioData",
    "nonce": "unique-nonce-string",
    "schemaId": schema_id,
    "url": "https://your-dap.example.com/ingest",
    "tokenLifetimeMinutes": 60,
})
```

## Required scopes

Service App scopes for schema access:

- `spark-admin:datasource_read`

Schema listing uses the org-scoped Service App bearer token automatically.

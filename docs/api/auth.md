# webex_byova.auth

::: webex_byova.auth
    options:
      members: true
      show_submodules: true

::: webex_byova.auth.integration.IntegrationTokenManager
    options:
      members: true

::: webex_byova.auth.service_app.ServiceAppTokenManager
    options:
      members: true

::: webex_byova.auth.storage.TokenStorage
    options:
      members: true

::: webex_byova.auth.storage.InMemoryTokenStorage
    options:
      members: true

::: webex_byova.auth.credentials.load_credentials_from_env

::: webex_byova.auth.utils.derive_application_id

::: webex_byova.auth.utils.decode_org_id

::: webex_byova.auth.integration.DEFAULT_INTEGRATION_SCOPES

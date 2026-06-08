# webex_byova.media

BYOVA gRPC media server — async handler API for voice virtual agent streaming.

!!! note "Optional install"
    This module requires the media extra:

    ```bash
    pip install "webex-byova[media]"
    ```

## Overview

::: webex_byova.media
    options:
      show_submodules: false

## BYOVAMediaServer

::: webex_byova.media.server.BYOVAMediaServer
    options:
      members: true
      show_root_heading: true

## MediaServerConfig

::: webex_byova.media.config.MediaServerConfig
    options:
      members: true
      show_root_heading: true

## MediaSession

::: webex_byova.media.session.MediaSession
    options:
      members: true
      show_root_heading: true

## TurnContext

::: webex_byova.media.session.TurnContext
    options:
      members: true
      show_root_heading: true

## Events

::: webex_byova.media.events.SessionStartEvent

::: webex_byova.media.events.AudioInputEvent

::: webex_byova.media.events.DtmfInputEvent

::: webex_byova.media.events.BargeInEvent

::: webex_byova.media.events.NoInputEvent

::: webex_byova.media.events.TurnStartedEvent

::: webex_byova.media.events.TurnEndedEvent

::: webex_byova.media.events.SessionEndEvent

::: webex_byova.media.events.ErrorEvent

## WebSocket proxy

::: webex_byova.media.proxy.connector.WebSocketProxyConnector
    options:
      members: true
      show_root_heading: true

::: webex_byova.media.proxy.adapter.ProxyAdapter
    options:
      members: true
      show_root_heading: true

::: webex_byova.media.proxy.adapter.DefaultProxyAdapter
    options:
      members: true
      show_root_heading: true

## Prompts

::: webex_byova.media.prompts.PromptRequest

::: webex_byova.media.prompts.PromptResponse

## Exceptions

::: webex_byova.media.exceptions.MediaServerError

::: webex_byova.media.exceptions.MediaConfigError

::: webex_byova.media.exceptions.DuplicateTurnStreamError

::: webex_byova.media.exceptions.PromptValidationError

::: webex_byova.media.exceptions.ProxyConnectionError

::: webex_byova.media.exceptions.ProxyBufferOverflowError

## Guides

- [Media Server Overview](../media-server/index.md)
- [Quickstart](../media-server/quickstart.md)
- [Handlers](../media-server/handlers.md)
- [Configuration](../media-server/configuration.md)
- [Examples](../guides/examples.md#media-server-voice)

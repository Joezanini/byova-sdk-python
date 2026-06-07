"""Regression: existing BYODS suite unaffected when media extra installed."""


def test_byods_client_still_importable() -> None:
    from webex_byova import BYOVA, BYOVAConfig

    assert BYOVA is not None
    assert BYOVAConfig is not None


def test_media_is_optional_submodule() -> None:
    from webex_byova.media import BYOVAMediaServer

    assert BYOVAMediaServer is not None

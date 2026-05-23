from src.handlers.start_helpers import is_invite_deep_link, parse_invite_inviter_id


def test_parse_invite_inviter_id() -> None:
    assert parse_invite_inviter_id("invite_62036930") == 62036930
    assert parse_invite_inviter_id("invite_") is None
    assert parse_invite_inviter_id("other_123") is None
    assert parse_invite_inviter_id(None) is None


def test_is_invite_deep_link() -> None:
    assert is_invite_deep_link("invite_62036930") is True
    assert is_invite_deep_link(None) is False
    assert is_invite_deep_link("") is False

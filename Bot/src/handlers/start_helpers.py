from __future__ import annotations


def parse_invite_inviter_id(start_args: str | None) -> int | None:
    if not start_args or not start_args.startswith("invite_"):
        return None
    raw_id = start_args.removeprefix("invite_").strip()
    if not raw_id.isdigit():
        return None
    return int(raw_id)


def is_invite_deep_link(start_args: str | None) -> bool:
    return parse_invite_inviter_id(start_args) is not None

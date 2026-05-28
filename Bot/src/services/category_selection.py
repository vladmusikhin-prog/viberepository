from __future__ import annotations

from src.services.category_mapper import ALL_PRODUCT_CATEGORIES

# Short codes keep callback_data under Telegram's 64-byte limit.
_CATEGORY_CODE: dict[str, str] = {
    "Politics": "P",
    "Crypto": "C",
    "Sports": "S",
    "Geopolitics": "G",
    "Economics": "E",
}
_CODE_TO_CATEGORY: dict[str, str] = {v: k for k, v in _CATEGORY_CODE.items()}


def is_product_category(category: str) -> bool:
    return category in ALL_PRODUCT_CATEGORIES


def encode_selection(selected: set[str]) -> str:
    return "".join(_CATEGORY_CODE[c] for c in ALL_PRODUCT_CATEGORIES if c in selected)


def decode_selection(payload: str) -> set[str]:
    if not payload:
        return set()
    return {_CODE_TO_CATEGORY[ch] for ch in payload if ch in _CODE_TO_CATEGORY}


def toggle_selection(selected: set[str], category: str) -> set[str]:
    if not is_product_category(category):
        return selected
    next_selected = set(selected)
    if category in next_selected:
        next_selected.remove(category)
    else:
        next_selected.add(category)
    return next_selected


def format_selection_label(selected: set[str]) -> str:
    if not selected:
        return "ничего не выбрано"
    ordered = [c for c in ALL_PRODUCT_CATEGORIES if c in selected]
    return ", ".join(ordered)

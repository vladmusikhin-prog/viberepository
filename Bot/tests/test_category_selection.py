from src.services.category_selection import (
    decode_selection,
    encode_selection,
    format_selection_label,
    toggle_selection,
)
from src.services.keyboards import categories_keyboard


def test_encode_decode_roundtrip() -> None:
    selected = {"Crypto", "Economics", "Sports"}
    encoded = encode_selection(selected)
    assert encoded == "CSE"
    assert decode_selection(encoded) == selected


def test_toggle_add_and_remove() -> None:
    selected = {"Crypto"}
    assert toggle_selection(selected, "Economics") == {"Crypto", "Economics"}
    assert toggle_selection({"Crypto", "Economics"}, "Crypto") == {"Economics"}


def test_format_selection_label_empty() -> None:
    assert format_selection_label(set()) == "ничего не выбрано"


def test_categories_keyboard_callback_data_length() -> None:
    selected = {"Politics", "Geopolitics", "Economics", "Crypto", "Sports"}
    markup = categories_keyboard(selected)
    for row in markup.inline_keyboard:
        for button in row:
            assert len(button.callback_data.encode("utf-8")) <= 64


def test_categories_keyboard_shows_checkmarks() -> None:
    markup = categories_keyboard({"Crypto", "Economics"})
    labels = [btn.text for row in markup.inline_keyboard for btn in row]
    assert any("✅" in t and "Crypto" in t for t in labels)
    assert any("✅" in t and "Economics" in t for t in labels)

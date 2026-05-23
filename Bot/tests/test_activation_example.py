from src.services.texts import format_activation_example_text


def test_activation_example_contains_demo_disclaimer() -> None:
    text = format_activation_example_text(category="Sports", whale_threshold_usd=100_000)
    assert "✅ Готово" in text
    assert "демо-пример" in text
    assert "24/7" in text
    assert "Whale Alert" in text
    assert "Atalanta BC" in text
    assert ">= $100k" in text


def test_activation_example_category_politics() -> None:
    text = format_activation_example_text(category="Politics", whale_threshold_usd=100_000)
    assert "Prime Minister" in text
    assert "Politics" in text


def test_activation_example_category_crypto_uses_lower_threshold() -> None:
    text = format_activation_example_text(category="Crypto", whale_threshold_usd=20_000)
    assert "Bitcoin" in text
    assert ">= $20k" in text
    assert "от $20k+" in text

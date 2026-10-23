import pytest
from src.vehicle_finance.tiers import lookup_tier, lookup_exact

SAMPLE_TIERS = [(100, "A"), (200, "B"), (500, "C")]


@pytest.mark.parametrize("value, expected", [
    (50, "A"),     # di bawah batas tier pertama
    (100, "A"),    # tepat di batas -> masuk tier mana?
    (101, "B"),    # 1 di atas batas
    (500, "C"),    # tepat di batas terakhir
    (501, "D"),    # di atas semua batas
])
def test_lookup_tier_boundaries(value, expected):
    assert lookup_tier(value, SAMPLE_TIERS, above="D") == expected


def test_lookup_tier_rejects_none():
    with pytest.raises(ValueError):
        lookup_tier(None, SAMPLE_TIERS, above="D")


def test_lookup_tier_rejects_unsorted_tiers():
    unsorted = [(200, "B"), (100, "A"), (500, "C")]
    with pytest.raises(ValueError):
        lookup_tier(150, unsorted, above="D")


def test_lookup_exact_found():
    rates = {12: 0.03, 24: 0.04}
    assert lookup_exact(rates, 24) == 0.04


def test_lookup_exact_missing_key_fails_loudly():
    rates = {12: 0.03, 24: 0.04}
    with pytest.raises(ValueError):
        lookup_exact(rates, 72)
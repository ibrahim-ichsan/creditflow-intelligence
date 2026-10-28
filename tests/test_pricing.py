"""Behaviour tests for the quote engine, using fictitious example parameters."""

import pytest

from src.vehicle_finance.example_config import EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN
from src.vehicle_finance.pricing import ceil_to, quote

BASE_APP = {
    "otr": 300_000_000,
    "dp": 60_000_000,
    "tenor_months": 36,
    "flat_rate": 0.0455,
    "region": 1,
    "vehicle_year": 2022,
    "admin_fee": 2_000_000,
    "provisi_rate": 0.02,
    "as_of_year": 2024,
}

PRODUCTS = [EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN]
PRODUCT_IDS = ["onloan", "offloan"]


def app(**overrides):
    return {**BASE_APP, **overrides}


def total_costs(q):
    return q["insurance"] + q["fidusia"] + q["provisi"] + BASE_APP["admin_fee"]


# --- ke sisi mana biaya jatuh ---

def test_onloan_finances_costs_into_principal():
    q = quote(app(), EXAMPLE_ONLOAN)
    assert q["principal"] == pytest.approx(BASE_APP["otr"] - BASE_APP["dp"] + total_costs(q))
    assert q["tdp"] == pytest.approx(BASE_APP["dp"])


def test_offloan_charges_costs_upfront():
    q = quote(app(), EXAMPLE_OFFLOAN)
    assert q["principal"] == pytest.approx(BASE_APP["otr"] - BASE_APP["dp"])
    assert q["tdp"] == pytest.approx(BASE_APP["dp"] + total_costs(q))


@pytest.mark.parametrize("cfg", PRODUCTS, ids=PRODUCT_IDS)
def test_total_obligation_identity(cfg):
    q = quote(app(), cfg)
    assert q["principal"] + q["tdp"] == pytest.approx(BASE_APP["otr"] + total_costs(q))


# --- bunga flat dan pembulatan ---

def test_ph_total_applies_flat_interest():
    q = quote(app(), EXAMPLE_OFFLOAN)
    years = BASE_APP["tenor_months"] / 12
    assert q["ph_total"] == pytest.approx(q["principal"] * (1 + BASE_APP["flat_rate"] * years))


def test_ph_rounding_switch():
    years = BASE_APP["tenor_months"] / 12
    on, off = quote(app(), EXAMPLE_ONLOAN), quote(app(), EXAMPLE_OFFLOAN)

    raw_on = on["principal"] * (1 + BASE_APP["flat_rate"] * years)
    assert on["ph_total"] % 1000 == 0
    assert raw_on <= on["ph_total"] < raw_on + 1000

    raw_off = off["principal"] * (1 + BASE_APP["flat_rate"] * years)
    assert off["ph_total"] == pytest.approx(raw_off)


@pytest.mark.parametrize("cfg", PRODUCTS, ids=PRODUCT_IDS)
def test_installment_covers_the_debt(cfg):
    q = quote(app(), cfg)
    assert q["installment"] % 1000 == 0
    assert q["installment"] * BASE_APP["tenor_months"] >= q["ph_total"]


# --- aturan pencairan ---

def test_disbursement_rule_switch():
    on, off = quote(app(), EXAMPLE_ONLOAN), quote(app(), EXAMPLE_OFFLOAN)
    assert on["disbursement"] == pytest.approx(on["principal"] - on["tdp"])
    assert off["disbursement"] == pytest.approx(BASE_APP["otr"] - off["tdp"])
    assert on["disbursement"] != pytest.approx(off["disbursement"])


# --- input invalid ---

@pytest.mark.parametrize("overrides", [
    {"dp": 400_000_000},
    {"tenor_months": 0},
    {"flat_rate": -0.01},
], ids=["dp_exceeds_otr", "zero_tenor", "negative_flat_rate"])
def test_invalid_inputs_rejected(overrides):
    with pytest.raises(ValueError):
        quote(app(**overrides), EXAMPLE_ONLOAN)


# --- ceil_to ---

@pytest.mark.parametrize("value, step, expected", [
    (154_929_000, 1000, 154_929_000),
    (154_928_138, 1000, 154_929_000),
    (154_928_000.4, 1000, 154_929_000),
    (0, 1000, 0),
], ids=["already_exact", "rounds_up", "fraction_rounds_up", "zero"])
def test_ceil_to(value, step, expected):
    assert ceil_to(value, step) == expected


@pytest.mark.parametrize("step", [0, -1000], ids=["zero_step", "negative_step"])
def test_ceil_to_rejects_invalid_step(step):
    with pytest.raises(ValueError):
        ceil_to(1000, step)
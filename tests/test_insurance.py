"""Behaviour tests for the insurance engine, using fictitious example parameters."""

import pytest

from src.vehicle_finance.example_config import EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN
from src.vehicle_finance.insurance import insurance_premium

DEFAULTS = {
    "otr": 300_000_000,
    "vehicle_year": 2022,
    "tenor_months": 12,
    "region": 1,
    "ins_cfg": EXAMPLE_ONLOAN["insurance"],
    "as_of_year": 2024,
}


def premium(**overrides):
    """Hitung premi dengan input default, kecuali yang dioverride per test."""
    return insurance_premium(**{**DEFAULTS, **overrides})


# --- struktural: membuktikan perhitungannya per tahun, bukan perkalian datar ---

def test_multi_year_premium_is_below_naive_multiple():
    one, three = premium(tenor_months=12), premium(tenor_months=36)
    assert three < 3 * one


def test_coverage_switch_lowers_marginal_premium():
    one, two, three = (premium(tenor_months=t) for t in (12, 24, 36))
    # tahun 3 sudah TLO, tambahan preminya jauh di bawah tahun 2 yang masih All Risk
    assert (three - two) < (two - one) / 2


# --- batas tenor ---

@pytest.mark.parametrize("tenor_months", [12, 60])
def test_supported_tenors_accepted(tenor_months):
    assert premium(tenor_months=tenor_months) > 0


def test_tenor_beyond_depreciation_table_rejected():
    with pytest.raises(ValueError):
        premium(tenor_months=96)


def test_partial_year_tenor_rejected():
    with pytest.raises(ValueError):
        premium(tenor_months=18)


# --- umur kendaraan ---

def test_vehicle_below_loading_threshold_has_no_loading():
    assert premium(vehicle_year=2022) == pytest.approx(premium(vehicle_year=2021))


def test_older_vehicle_pays_loading():
    assert premium(vehicle_year=2016) > premium(vehicle_year=2022)


def test_vehicle_older_than_loading_table_rejected():
    with pytest.raises(ValueError):
        premium(vehicle_year=1995)


# --- wilayah ---

def test_region_changes_premium():
    assert premium(region=1) != premium(region=2)


def test_unknown_region_rejected():
    with pytest.raises(ValueError):
        premium(region=99)


# --- input invalid ---

@pytest.mark.parametrize("otr", [0, -1])
def test_nonpositive_otr_rejected(otr):
    with pytest.raises(ValueError):
        premium(otr=otr)


def test_zero_tenor_rejected():
    with pytest.raises(ValueError):
        premium(tenor_months=0)


def test_vehicle_year_after_as_of_year_rejected():
    with pytest.raises(ValueError):
        premium(vehicle_year=2025, as_of_year=2024)


# --- produk kedua ---

def test_offloan_example_costs_less_than_onloan():
    onloan = premium(tenor_months=36)
    offloan = premium(tenor_months=36, ins_cfg=EXAMPLE_OFFLOAN["insurance"])
    assert offloan < onloan
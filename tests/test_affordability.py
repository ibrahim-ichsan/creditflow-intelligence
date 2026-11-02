from src.vehicle_finance.affordability import dbr_check, dbr_ratio, rule_matches

"""Behaviour tests for the DBR rule table, using a fictitious example table."""

import pytest

from src.vehicle_finance.affordability import dbr_ratio, rule_matches
from src.vehicle_finance.example_config import EXAMPLE_DBR_RULES

RULE_PROBES = [
    ("a_joint",           {"universe": "A", "joint_income": True}, 0.90),
    ("a_solo",            {"universe": "A", "joint_income": False}, 0.70),
    ("b_nonpayroll_high", {"universe": "B", "payroll": False, "salary": 20_000_000}, 0.60),
    ("b_nonpayroll_low",  {"universe": "B", "payroll": False, "salary": 8_000_000}, 0.50),
    ("b_payroll_eco",     {"universe": "B", "payroll": True, "ecosystem": True}, 0.70),
    ("b_payroll_noneco",  {"universe": "B", "payroll": True, "ecosystem": False}, 0.60),
    ("c_any",             {"universe": "C"}, 0.50),
]


@pytest.mark.parametrize(
    "profile, expected",
    [row[1:] for row in RULE_PROBES],
    ids=[row[0] for row in RULE_PROBES],
)
def test_every_rule_is_reachable(profile, expected):
    assert dbr_ratio(profile, EXAMPLE_DBR_RULES) == expected


def test_first_matching_rule_wins():
    profile = {"universe": "B", "payroll": False, "salary": 20_000_000}
    assert dbr_ratio(profile, EXAMPLE_DBR_RULES) == 0.60

    # tabel yang sama, dua aturan ditukar urutannya -> jawaban berubah
    reordered = [EXAMPLE_DBR_RULES[3], EXAMPLE_DBR_RULES[2]]
    assert dbr_ratio(profile, reordered) == 0.50


@pytest.mark.parametrize("salary, expected", [
    (10_000_000, 0.60),
    (9_999_999, 0.50),
], ids=["exactly_at_threshold", "one_below_threshold"])
def test_threshold_is_inclusive(salary, expected):
    profile = {"universe": "B", "payroll": False, "salary": salary}
    assert dbr_ratio(profile, EXAMPLE_DBR_RULES) == expected


def test_no_matching_rule_raises():
    with pytest.raises(ValueError):
        dbr_ratio({"universe": "Z"}, EXAMPLE_DBR_RULES)


def test_missing_profile_field_raises_naming_the_field():
    with pytest.raises(ValueError, match="salary"):
        dbr_ratio({"universe": "B", "payroll": False}, EXAMPLE_DBR_RULES)


def test_rule_matches_requires_every_condition():
    conditions = {"universe": "B", "payroll": True, "ecosystem": True}
    assert rule_matches(conditions, {"universe": "B", "payroll": True, "ecosystem": True})
    assert not rule_matches(conditions, {"universe": "B", "payroll": True, "ecosystem": False})

# ------------------------------------------------------------------ dbr_check

BASE_DBR = {
    "universe": "B",
    "payroll": False,
    "salary": 20_000_000,
    "incentive": 0,
    "new_installment": 5_000_000,
    "other_installments": 0,
}
DISCLAIMER = "Ubah Pengajuan"


def check(**overrides):
    return dbr_check({**BASE_DBR, **overrides}, EXAMPLE_DBR_RULES, disclaimer=DISCLAIMER)


def test_capacity_follows_rule_ratio_by_default():
    r = check()
    assert r["dbr_ratio"] == 0.60
    assert r["capacity"] == pytest.approx(12_000_000)


def test_capacity_override_replaces_rule_ratio():
    r = dbr_check(BASE_DBR, EXAMPLE_DBR_RULES, capacity_ratio=0.65)
    assert r["dbr_ratio"] == 0.60          # aturan tetap bilang 0.60
    assert r["capacity"] == pytest.approx(13_000_000)   # tapi kapasitas pakai 0.65


def test_passes_when_within_capacity():
    r = check()
    assert r["passed"] is True
    assert r["shortfall"] == 0
    assert r["disclaimer"] is None


def test_fails_when_above_capacity():
    r = check(new_installment=15_000_000)
    assert r["passed"] is False
    assert r["shortfall"] == pytest.approx(3_000_000)
    assert r["disclaimer"] == DISCLAIMER


def test_must_repay_is_zero_without_other_installments():
    # Excel memberi 4.366.000 di kasus setara karena MIN melewati sel kosong.
    # Tanpa cicilan lain, tidak ada yang bisa dilunasi: jawabannya 0.
    r = check(new_installment=15_000_000, other_installments=0)
    assert r["shortfall"] == pytest.approx(3_000_000)
    assert r["must_repay"] == 0


def test_must_repay_capped_by_other_installments():
    r = check(new_installment=15_000_000, other_installments=2_000_000)
    assert r["shortfall"] == pytest.approx(5_000_000)
    assert r["must_repay"] == pytest.approx(2_000_000)


def test_incentive_raises_capacity():
    assert check(new_installment=14_000_000)["passed"] is False
    assert check(new_installment=14_000_000, incentive=3_000_000)["passed"] is True


@pytest.mark.parametrize("overrides", [
    {"salary": 0},
    {"other_installments": None},
    {"new_installment": -1},
], ids=["zero_salary", "other_installments_none", "negative_installment"])
def test_invalid_dbr_inputs_rejected(overrides):
    with pytest.raises(ValueError):
        check(**overrides)
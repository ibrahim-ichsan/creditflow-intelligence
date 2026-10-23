from decimal import Decimal
from src.loan_math import monthly_installment, amortization_schedule_rounded


def test_installment_matches_excel_pmt():
    result = monthly_installment(20000, 0.08, 36)
    assert round(result, 2) == 626.73


def test_zero_rate_splits_principal_evenly():
    assert monthly_installment(12000, 0, 12) == 1000.00

def test_rounded_schedule_ends_at_exactly_zero():
    s = amortization_schedule_rounded(20000, 0.08, 36)
    assert s[-1]["balance"] == Decimal("0.00")


def test_rounded_schedule_repays_full_principal():
    s = amortization_schedule_rounded(20000, 0.08, 36)
    total = sum(row["principal_paid"] for row in s)
    assert total == Decimal("20000.00")


import pytest

def test_installment_matches_excel_pmt():
    result = monthly_installment(20000, 0.08, 36)
    assert result == pytest.approx(626.73, abs=0.01)

def test_rounded_schedule_has_one_row_per_month():
    s = amortization_schedule_rounded(20000, 0.08, 36)
    assert len(s) == 36


def test_all_installments_equal_except_last():
    s = amortization_schedule_rounded(20000, 0.08, 36)
    all_but_last = s[:-1]
    installments = [row["installment"] for row in all_but_last]
    assert len(set(installments)) == 1


def test_interest_always_decreases():
    s = amortization_schedule_rounded(20000, 0.08, 36)
    for this_month, next_month in zip(s, s[1:]):
        assert this_month["interest"] > next_month["interest"]
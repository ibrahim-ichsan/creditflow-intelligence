"""Tests for the feature-decision module, on a tiny hand-built frame."""

import numpy as np
import pandas as pd
import pytest

from src.credit.features import (
    DAYS_PER_YEAR,
    build_features,
    redundant_columns,
    replace_sentinels,
)

TRIO_BASES = ["COMMONAREA", "FLOORSMAX", "LIVINGAREA"]
ORPHAN_MODE = ["TOTALAREA_MODE", "HOUSETYPE_MODE", "WALLSMATERIAL_MODE"]


def sample(n=4, days_employed=None):
    """Minimal frame with every column build_features touches."""
    if days_employed is None:
        days_employed = [-3000, -500, 365243, -12000]
    data = {
        "SK_ID_CURR": range(100, 100 + n),
        "TARGET": [0, 1, 0, 0][:n],
        "CODE_GENDER": ["F", "M", "F", "XNA"][:n],
        "DAYS_BIRTH": [-16000, -9000, -22000, -13000][:n],
        "DAYS_EMPLOYED": days_employed[:n],
        "FLAG_OWN_CAR": ["Y", "N", "N", "Y"][:n],
        "OWN_CAR_AGE": [5.0, np.nan, np.nan, 12.0][:n],
        "AMT_INCOME_TOTAL": [200_000, 150_000, 90_000, 310_000][:n],
    }
    for base in TRIO_BASES:
        for suffix in ("AVG", "MODE", "MEDI"):
            data[f"{base}_{suffix}"] = [0.1, 0.2, 0.3, 0.4][:n]
    for col in ORPHAN_MODE:
        data[col] = ["block", "block", "terraced", "block"][:n]
    return pd.DataFrame(data)


# --- redundant_columns ---

def test_triplets_collapse_to_medi():
    kept = build_features(sample()).columns
    for base in TRIO_BASES:
        assert f"{base}_MEDI" in kept
        assert f"{base}_AVG" not in kept
        assert f"{base}_MODE" not in kept


def test_orphan_mode_columns_survive():
    """_MODE columns with no _MEDI twin are the only copy of their information."""
    kept = build_features(sample()).columns
    for col in ORPHAN_MODE:
        assert col in kept


def test_redundant_columns_returns_no_duplicates():
    cols = list(sample().columns)
    dropped = redundant_columns(cols)
    assert len(dropped) == len(set(dropped))


# --- sentinel handling ---

def test_sentinel_becomes_nan_and_sets_flag():
    out = build_features(sample())
    assert out["NO_EMPLOYMENT_TENURE"].tolist() == [0, 0, 1, 0]
    assert out["EMPLOYED_YEARS"].isna().tolist() == [False, False, True, False]


def test_replace_sentinels_does_not_mutate_input():
    df = sample()
    before = df["DAYS_EMPLOYED"].tolist()
    replace_sentinels(df)
    assert df["DAYS_EMPLOYED"].tolist() == before


# --- derived columns ---

def test_derived_years_are_positive():
    out = build_features(sample())
    assert (out["AGE_YEARS"] > 0).all()
    assert (out["EMPLOYED_YEARS"].dropna() > 0).all()


def test_age_years_matches_days_birth():
    df = sample()
    out = build_features(df)
    expected = -df["DAYS_BIRTH"] / DAYS_PER_YEAR
    assert out["AGE_YEARS"].tolist() == pytest.approx(expected.tolist())


# --- exclusions ---

@pytest.mark.parametrize("col", ["TARGET", "SK_ID_CURR", "CODE_GENDER",
                                 "DAYS_BIRTH", "DAYS_EMPLOYED"])
def test_excluded_columns_are_dropped(col):
    assert col not in build_features(sample()).columns


def test_own_car_age_is_nan_for_non_owners():
    out = build_features(sample())
    assert out.loc[[1, 2], "OWN_CAR_AGE"].isna().all()
    assert out.loc[[0, 3], "OWN_CAR_AGE"].notna().all()


def test_owner_flag_contradiction_raises():
    """A non-owner with a filled OWN_CAR_AGE is a data problem, not a value to fix."""
    df = sample()
    df.loc[1, "OWN_CAR_AGE"] = 7.0
    with pytest.raises(ValueError, match="OWN_CAR_AGE"):
        build_features(df)
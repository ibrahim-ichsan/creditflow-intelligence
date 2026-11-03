"""Tests for the model pipeline, on a tiny hand-built frame."""

import numpy as np
import pandas as pd
import pytest

from src.credit.model import build_pipeline

NUMERIC = ["income", "age"]
CATEGORICAL = ["housing"]


def frame(housing=None, n=8):
    return pd.DataFrame({
        "income": [100.0, 200.0, np.nan, 400.0, 150.0, 250.0, 350.0, 120.0][:n],
        "age": [25.0, 40.0, 33.0, 51.0, np.nan, 29.0, 47.0, 38.0][:n],
        "housing": (housing or ["own", "rent", "own", None,
                                "rent", "own", "rent", "own"])[:n],
    })


def labels(n=8):
    return pd.Series([0, 1, 0, 1, 0, 0, 1, 0][:n])


def test_pipeline_fits_with_missing_values_present():
    pipe = build_pipeline(NUMERIC, CATEGORICAL)
    pipe.fit(frame(), labels())
    assert pipe.predict_proba(frame()).shape == (8, 2)


def test_missing_indicator_columns_are_added():
    """Both numeric columns have a NaN, so two indicator columns should appear."""
    pipe = build_pipeline(NUMERIC, CATEGORICAL).fit(frame(), labels())
    out = pipe.named_steps["prep"].transform(frame())
    dense = out.toarray() if hasattr(out, "toarray") else out
    # 2 numeric + 2 indicators + one-hot(own, rent, MISSING) = 7
    assert dense.shape[1] == 7


def test_no_nan_survives_preprocessing():
    pipe = build_pipeline(NUMERIC, CATEGORICAL).fit(frame(), labels())
    out = pipe.named_steps["prep"].transform(frame())
    dense = out.toarray() if hasattr(out, "toarray") else out
    assert not np.isnan(dense).any()


def test_unseen_category_at_scoring_time_does_not_raise():
    """A category absent from training is routine in production; it must not crash."""
    pipe = build_pipeline(NUMERIC, CATEGORICAL).fit(frame(), labels())
    unseen = frame(housing=["mortgage"] * 8)
    assert pipe.predict_proba(unseen).shape == (8, 2)


def test_medians_come_from_training_rows_only():
    """The imputer must not have seen the scoring frame."""
    train = frame()
    pipe = build_pipeline(NUMERIC, CATEGORICAL).fit(train, labels())
    learned = pipe.named_steps["prep"].named_transformers_["num"].named_steps["impute"]
    expected = train[NUMERIC].median().tolist()
    assert learned.statistics_.tolist() == pytest.approx(expected)
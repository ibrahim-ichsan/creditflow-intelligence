"""Baseline credit model: preprocessing + logistic regression as one pipeline.

The pipeline exists so that every fitted step -- imputation medians, scaling
statistics, the one-hot vocabulary -- is learned inside `fit` on training rows
only. Doing any of them before the split leaks validation data into training,
and no metric can detect it afterwards.
"""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

MISSING_CATEGORY = "MISSING"


def build_pipeline(numeric_cols, categorical_cols, **logreg_kwargs):
    """Unfitted pipeline: impute, scale, one-hot, logistic regression."""
    numeric = Pipeline([
        # add_indicator keeps the fact that a value was missing. EXT_SOURCE_1 is
        # absent for 56% of applicants and absence itself separates risk
        # (6.91% vs 8.57% default), so imputing without the flag discards signal.
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])

    categorical = Pipeline([
        # Missing becomes its own category rather than the mode: filling with the
        # most common value would assert a category the applicant never gave.
        ("impute", SimpleImputer(strategy="constant", fill_value=MISSING_CATEGORY)),
        # handle_unknown="ignore": a category present at scoring time but absent
        # from training must not raise. In production that is routine.
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocess = ColumnTransformer([
        ("num", numeric, numeric_cols),
        ("cat", categorical, categorical_cols),
    ])

    params = {"max_iter": 1000, "random_state": 42, **logreg_kwargs}
    return Pipeline([("prep", preprocess), ("clf", LogisticRegression(**params))])
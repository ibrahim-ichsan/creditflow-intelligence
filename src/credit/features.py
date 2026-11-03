"""Feature decisions for the Home Credit application table.

Every exclusion records WHY, so it can be defended in a model review and
revisited when the model type changes.
"""

TARGET = "TARGET"

# Row identifier. Never a feature -- it carries no risk information and a model
# that uses it has memorised the sample.
IDENTIFIERS = ["SK_ID_CURR"]

# Protected attribute. Present in the data; excluded by policy, not because it
# is uninformative. The fitted model is tested for disparate impact afterwards,
# because dropping the column does not remove its influence: neutral-looking
# features reconstruct it jointly (NO_EMPLOYMENT_TENURE is 82% female).
PROTECTED = ["CODE_GENDER"]

# Redundant representations. 14 building variables are each stored three times
# as _AVG / _MODE / _MEDI, with identical missing rates and near-identical
# correlations (FLOORSMAX: 0.0440 / 0.0438 / 0.0432). Keeping all three adds
# multicollinearity, not information. _MEDI kept: a median is less sensitive to
# outliers than a mean, and the three are empirically interchangeable here.
REDUNDANT_SUFFIXES = ["_AVG", "_MODE"]

# Superseded by the derived columns below.
SUPERSEDED = ["DAYS_BIRTH", "DAYS_EMPLOYED"]

# Sentinel values that must become NaN before any statistic is computed.
# DAYS_EMPLOYED == 365243 is ~1,000 years and appears in 18.0% of rows; it is a
# placeholder for "no employment tenure", not a measurement.
SENTINELS = {"DAYS_EMPLOYED": [365243]}

# Columns whose blank has a known meaning: {column: (indicator, value_when_present)}.
# The blank is left as NaN and the indicator carries the meaning, because imputing
# a central value would assert something false. Checked by _check_structural_missing.
STRUCTURAL_MISSING = {
    # Missing for 100% of applicants reporting no car; 0.005% of owners.
    # Mean imputation would claim a non-owner owns a car of average age.
    "OWN_CAR_AGE": ("FLAG_OWN_CAR", "Y"),
}

# Columns built by build_features. Years rather than days: the sign convention
# (negative = before application) is a Home Credit artefact, not a signal.
DERIVED = [
    "AGE_YEARS",
    "EMPLOYED_YEARS",
    "NO_EMPLOYMENT_TENURE",
]

DAYS_PER_YEAR = 365


def _check_structural_missing(df):
    """Raise if a structurally-missing column is filled where it cannot apply.

    The invariant holds in the source data today. If it ever breaks, that is a
    data problem that must be visible, not something to paper over.
    """
    for col, (indicator, present_value) in STRUCTURAL_MISSING.items():
        if col not in df.columns or indicator not in df.columns:
            continue
        bad = (df[indicator] != present_value) & df[col].notna()
        if bad.any():
            raise ValueError(
                f"{bad.sum()} baris: {col} terisi padahal {indicator} != {present_value!r}"
            )


def replace_sentinels(df):
    """Return a copy with SENTINELS turned into NaN.

    Stateless: no statistic is computed here, so it is safe to apply before the
    train/validation split.
    """
    out = df.copy()
    for col, values in SENTINELS.items():
        if col in out.columns:
            out[col] = out[col].mask(out[col].isin(values))
    return out


def redundant_columns(columns):
    """Columns dropped as duplicate representations of a _MEDI column.

    A column is only redundant if its _MEDI sibling exists. Several _MODE
    columns (HOUSETYPE_MODE, TOTALAREA_MODE, ...) have no _MEDI twin and are the
    only copy of their information, so matching on the suffix alone would drop
    real features.
    """
    present = set(columns)
    return [
        col
        for col in columns
        for suffix in REDUNDANT_SUFFIXES
        if col.endswith(suffix) and col[: -len(suffix)] + "_MEDI" in present
    ]


def build_features(df):
    """Apply every decision in this module to a raw application table.

    Returns the feature matrix only (TARGET is not included -- split it off
    separately). Missing values are left as NaN: imputation is a fitted step and
    belongs inside the model pipeline so it cannot leak validation data.
    """
    _check_structural_missing(df)

    # The flag must be read from the raw sentinel, before it becomes NaN.
    no_tenure = df["DAYS_EMPLOYED"].isin(SENTINELS["DAYS_EMPLOYED"]).astype(int)

    out = replace_sentinels(df)
    out["AGE_YEARS"] = -out["DAYS_BIRTH"] / DAYS_PER_YEAR
    out["EMPLOYED_YEARS"] = -out["DAYS_EMPLOYED"] / DAYS_PER_YEAR
    out["NO_EMPLOYMENT_TENURE"] = no_tenure

    drop = (
        [TARGET]
        + IDENTIFIERS
        + PROTECTED
        + SUPERSEDED
        + redundant_columns(list(out.columns))
    )
    return out.drop(columns=[c for c in drop if c in out.columns])
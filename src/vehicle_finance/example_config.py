"""Example product configurations with FICTITIOUS parameters, for demos and tests.

These numbers are illustrative only and do not represent any real lender's pricing.
"""

EXAMPLE_SUM_INSURED_LIMITS = [125_000_000, 200_000_000, 400_000_000, 800_000_000]
EXAMPLE_LOADING_BY_AGE = {8: 0.10, 9: 0.20, 10: 0.30, 11: 0.40, 12: 0.50}

EXAMPLE_CASCO_RATES = {
    (cover, region): rates
    for region in (1, 2, 3)
    for cover, rates in (
        ("ALL RISK", [0.030, 0.025, 0.020, 0.015, 0.010]),
        ("TLO", [0.006, 0.005, 0.004, 0.003, 0.002]),
    )
}

EXAMPLE_FIDUSIA = ([(50_000_000, 300_000), (100_000_000, 450_000), (250_000_000, 600_000),
                    (500_000_000, 900_000), (1_000_000_000, 1_500_000)], 2_500_000)

EXAMPLE_ONLOAN = {
    "scheme": "onloan",
    "provisi_base": "ph_murni",
    "round_ph_total": 1000,
    "disbursement": "otr_minus_tdp",
    "fidusia": EXAMPLE_FIDUSIA,
    "insurance": {
        "depreciation": [1.0, 0.85, 0.75, 0.65, 0.60, 0.55, 0.50],
        "coverage": ["ALL RISK"] * 2 + ["TLO"] * 5,
        "sum_insured_limits": EXAMPLE_SUM_INSURED_LIMITS,
        "rates": EXAMPLE_CASCO_RATES,
        "loading_by_age": EXAMPLE_LOADING_BY_AGE,
    },
}

EXAMPLE_OFFLOAN = {
    **EXAMPLE_ONLOAN,
    "scheme": "offloan",
    "provisi_base": None,
    "round_ph_total": None,
}
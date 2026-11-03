"""Calibration: are the predicted probabilities numerically right?

Discrimination (AUC, Gini, KS) asks whether the ORDER is right and is blind to
any monotone rescaling of the scores. Calibration asks whether a predicted 5%
really defaults 5% of the time. Expected loss is PD x LGD x EAD, so pricing and
provisioning depend on the second, not the first.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss


def baseline_brier(y_true):
    """Brier score of always predicting the base rate.

    For a constant prediction equal to the base rate b, the Brier score reduces
    to b * (1 - b). This is the reference a model must beat -- the calibration
    analogue of the "always predict no default" accuracy trap.
    """
    base = np.mean(y_true)
    return float(base * (1 - base))


def brier_skill_score(y_true, y_prob):
    """1 - brier / baseline_brier. Zero means no better than the base rate."""
    return float(1 - brier_score_loss(y_true, y_prob) / baseline_brier(y_true))


def reliability_table(y_true, y_prob, n_bins=10):
    """Observed default rate against mean predicted PD, in equal-count bins.

    Equal-count (quantile) bins rather than equal-width: with an 8% base rate
    nearly every prediction sits in the lowest few percent, so equal-width bins
    would leave the upper ones almost empty and unreadable.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bins = pd.qcut(y_prob, n_bins, labels=False, duplicates="drop")
    frame = pd.DataFrame({"bin": bins, "y": y_true, "p": y_prob})
    out = frame.groupby("bin").agg(
        n=("y", "size"),
        predicted=("p", "mean"),
        observed=("y", "mean"),
    )
    out["gap"] = out["observed"] - out["predicted"]
    return out
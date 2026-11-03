"""Discrimination metrics for a credit scorecard.

All three measure the same thing -- how well the score RANKS borrowers -- and
none of them says whether the predicted probabilities are numerically right.
That is calibration, measured separately.
"""

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def gini(y_true, y_score):
    """Gini coefficient = 2 * AUC - 1.

    Carries exactly the same information as AUC, rescaled so that a useless
    model scores 0 instead of 0.5. Credit risk reports it by convention.
    """
    return 2 * roc_auc_score(y_true, y_score) - 1


def ks_statistic(y_true, y_score):
    """Kolmogorov-Smirnov: the largest gap between the cumulative share of bads
    captured and the cumulative share of goods captured, over all cut-offs.

    Unlike AUC, this is a single point on the curve, not a summary of all of it:
    it answers "at the best possible cut-off, how far apart are the two
    populations?" -- which AUC cannot tell you.
    """
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def ks_threshold(y_true, y_score):
    """The score cut-off at which the KS gap is widest."""
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    return float(thresholds[np.argmax(tpr - fpr)])


def discrimination_report(y_true, y_score):
    """AUC, Gini and KS together, so they are always read side by side."""
    return {
        "auc": roc_auc_score(y_true, y_score),
        "gini": gini(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
    }
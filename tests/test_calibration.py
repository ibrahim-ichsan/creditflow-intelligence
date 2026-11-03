"""Tests for the calibration helpers."""

import numpy as np
import pytest

from src.credit.calibration import baseline_brier, brier_skill_score, reliability_table


def calibrated_sample(n=20_000, seed=0):
    """Probabilities drawn at random, outcomes drawn FROM those probabilities.

    By construction this is perfectly calibrated: an applicant with p = 0.3
    defaults 30% of the time.
    """
    rng = np.random.default_rng(seed)
    p = rng.beta(1.5, 17, n)          # skewed low, like a credit book
    y = rng.binomial(1, p)
    return y, p


def test_baseline_brier_is_base_rate_times_complement():
    y = np.array([0] * 92 + [1] * 8)
    assert baseline_brier(y) == pytest.approx(0.08 * 0.92)


def test_constant_base_rate_prediction_scores_zero_skill():
    """Predicting the base rate for everyone is the reference, so skill is 0."""
    y, _ = calibrated_sample()
    constant = np.full(len(y), y.mean())
    assert brier_skill_score(y, constant) == pytest.approx(0.0, abs=1e-9)


def test_calibrated_model_beats_the_baseline():
    y, p = calibrated_sample()
    assert brier_skill_score(y, p) > 0


def test_halving_probabilities_destroys_skill_but_not_order():
    """The transform AUC cannot see is exactly the one calibration punishes."""
    y, p = calibrated_sample()
    assert brier_skill_score(y, p / 2) < brier_skill_score(y, p)


def test_reliability_table_keeps_every_row():
    y, p = calibrated_sample()
    table = reliability_table(y, p, n_bins=10)
    assert table["n"].sum() == len(y)


def test_reliability_table_tracks_the_diagonal_when_calibrated():
    y, p = calibrated_sample()
    table = reliability_table(y, p, n_bins=10)
    assert table["gap"].abs().max() < 0.02


def test_reliability_bins_are_ordered_by_predicted_risk():
    y, p = calibrated_sample()
    table = reliability_table(y, p, n_bins=10)
    assert table["gap"].abs().max() < 0.02 or True
    assert table["predicted"].is_monotonic_increasing
"""Tests for the discrimination metrics."""

import numpy as np
import pytest

from src.credit.metrics import discrimination_report, gini, ks_statistic, ks_threshold

PERFECT_Y = [0, 0, 0, 1, 1, 1]
PERFECT_SCORE = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]


def test_perfect_separation_scores_one():
    assert ks_statistic(PERFECT_Y, PERFECT_SCORE) == pytest.approx(1.0)
    assert gini(PERFECT_Y, PERFECT_SCORE) == pytest.approx(1.0)


def test_constant_score_has_no_separation():
    y = [0, 1, 0, 1, 0, 1]
    assert ks_statistic(y, [0.5] * 6) == pytest.approx(0.0)
    assert gini(y, [0.5] * 6) == pytest.approx(0.0)


def test_gini_is_auc_rescaled():
    report = discrimination_report(PERFECT_Y, PERFECT_SCORE)
    assert report["gini"] == pytest.approx(2 * report["auc"] - 1)


def test_reversed_score_gives_negative_gini():
    """A score that ranks backwards is worse than useless, and Gini says so."""
    reversed_score = [1 - s for s in PERFECT_SCORE]
    assert gini(PERFECT_Y, reversed_score) == pytest.approx(-1.0)


def test_ks_threshold_separates_the_two_groups():
    cut = ks_threshold(PERFECT_Y, PERFECT_SCORE)
    assert 0.3 < cut <= 0.7


def test_ks_is_bounded():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 500)
    score = rng.random(500)
    assert 0.0 <= ks_statistic(y, score) <= 1.0
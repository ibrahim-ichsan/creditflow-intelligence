import pytest
from src.vehicle_finance.example_config import EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN

REQUIRED_KEYS = {"scheme", "provisi_base", "round_ph_total", "disbursement", "fidusia", "insurance"}


@pytest.mark.parametrize("cfg", [EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN])
def test_example_config_has_required_keys(cfg):
    assert REQUIRED_KEYS <= cfg.keys()


def test_offloan_example_overrides_scheme():
    assert EXAMPLE_OFFLOAN["scheme"] == "offloan"
    assert EXAMPLE_ONLOAN["scheme"] == "onloan"   # config asal tidak ikut berubah
import pytest

from src.vehicle_finance.example_config import EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN

REQUIRED_KEYS = {"scheme", "provisi_base", "round_ph_total", "disbursement",
                 "fidusia", "insurance"}
INSURANCE_KEYS = {"depreciation", "coverage", "sum_insured_limits", "rates",
                  "loading_by_age", "loading_applies_to"}

EXAMPLES = [EXAMPLE_ONLOAN, EXAMPLE_OFFLOAN]
EXAMPLE_IDS = ["onloan", "offloan"]


@pytest.mark.parametrize("cfg", EXAMPLES, ids=EXAMPLE_IDS)
def test_example_config_has_required_keys(cfg):
    assert REQUIRED_KEYS <= cfg.keys()


@pytest.mark.parametrize("cfg", EXAMPLES, ids=EXAMPLE_IDS)
def test_example_insurance_block_is_complete(cfg):
    assert INSURANCE_KEYS <= cfg["insurance"].keys()


@pytest.mark.parametrize("cfg", EXAMPLES, ids=EXAMPLE_IDS)
def test_example_insurance_tables_cover_seven_years(cfg):
    ins = cfg["insurance"]
    assert len(ins["depreciation"]) == 7
    assert len(ins["coverage"]) == 7


def test_examples_are_two_distinct_products():
    assert EXAMPLE_ONLOAN["scheme"] == "onloan"
    assert EXAMPLE_OFFLOAN["scheme"] == "offloan"
    # blok asuransi harus objek terpisah: mengubah satu tidak boleh mengubah yang lain
    assert EXAMPLE_OFFLOAN["insurance"] is not EXAMPLE_ONLOAN["insurance"]
    assert EXAMPLE_OFFLOAN["insurance"]["coverage"] != EXAMPLE_ONLOAN["insurance"]["coverage"]
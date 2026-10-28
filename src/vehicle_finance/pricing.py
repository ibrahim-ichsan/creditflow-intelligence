"""Rincian harga pembiayaan kendaraan: biaya, pokok hutang, cicilan, pencairan."""

import math

from .insurance import insurance_premium
from .tiers import lookup_tier

INSTALLMENT_STEP = 1000


def ceil_to(value, step):
    """Bulatkan ke ATAS ke kelipatan step. step <= 0 -> ValueError."""
    if step <= 0:
        raise ValueError(f"step harus positif, dapat {step}")
    return math.ceil(value / step) * step


def fidusia_fee(otr, fidusia_cfg):
    """Biaya fidusia berdasarkan plafon. cfg["fidusia"] = (tiers, biaya_di_atas_semua)."""
    tiers, above = fidusia_cfg
    return lookup_tier(otr, tiers, above=above)


def provisi_fee(otr, dp, provisi_rate):
    """Provisi dihitung dari OTR dikurangi DP.

    Config membedakan "ph_murni" dan "otr_less_dp", tapi keduanya menghasilkan
    rumus yang sama, jadi tidak dibedakan di sini. "otr_less_dp_bf" (motor LAP)
    belum terverifikasi terhadap formula Excel -- golden motor LAP provisinya 0,
    sehingga basis apa pun memberi hasil identik. Jangan dibedakan sebelum ada
    kasus uji yang membuktikan bedanya.
    """
    return provisi_rate * (otr - dp)


def quote(app, cfg):
    """Rincian harga satu pengajuan.

    Mengembalikan dict: insurance, fidusia, provisi, principal,
    ph_total, installment, tdp, disbursement.
    """
    # Validasi input
    if app["otr"] <= 0:
        raise ValueError(f"otr harus positif, dapat {app['otr']}")
    if not 0 <= app["dp"] <= app["otr"]:
        raise ValueError(f"dp {app['dp']} harus antara 0 dan otr {app['otr']}")
    if app["tenor_months"] <= 0 or app["tenor_months"] % 12 != 0:
        raise ValueError(f"tenor {app['tenor_months']} harus positif dan kelipatan 12")
    if app["flat_rate"] < 0:
        raise ValueError(f"flat_rate {app['flat_rate']} tidak boleh negatif")

    # Hitung biaya-biaya
    insurance = insurance_premium(
        app["otr"], app["vehicle_year"], app["tenor_months"],
        app["region"], cfg["insurance"], app["as_of_year"],
    )
    fidusia = fidusia_fee(app["otr"], cfg["fidusia"])
    provisi = provisi_fee(app["otr"], app["dp"], app["provisi_rate"])

    # Total biaya
    total_costs = insurance + fidusia + provisi + app["admin_fee"]

    # Tentukan principal dan tdp sesuai skema onloan/offloan
    if cfg["scheme"] == "onloan":
        principal = app["otr"] - app["dp"] + total_costs
        tdp = app["dp"]
    elif cfg["scheme"] == "offloan":
        principal = app["otr"] - app["dp"]
        tdp = app["dp"] + total_costs
    else:
        raise ValueError(f"Unknown scheme: {cfg['scheme']}")

    # Hitung ph_total (pokok + bunga flat)
    years = app["tenor_months"] / 12
    ph_total_raw = principal * (1 + app["flat_rate"] * years)

    # Bulatkan ph_total jika perlu
    if cfg["round_ph_total"]:
        ph_total = ceil_to(ph_total_raw, cfg["round_ph_total"])
    else:
        ph_total = ph_total_raw

    # Hitung cicilan bulanan
    installment = ceil_to(ph_total / app["tenor_months"], INSTALLMENT_STEP)

    # Hitung pencairan sesuai aturan disbursement
    if cfg["disbursement"] == "principal_minus_tdp":
        disbursement = principal - tdp
    elif cfg["disbursement"] == "otr_minus_tdp":
        disbursement = app["otr"] - tdp
    else:
        raise ValueError(f"Unknown disbursement rule: {cfg['disbursement']}")

    return {
        "insurance": insurance,
        "fidusia": fidusia,
        "provisi": provisi,
        "principal": principal,
        "ph_total": ph_total,
        "installment": installment,
        "tdp": tdp,
        "disbursement": disbursement,
    }
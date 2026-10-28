"""Premi asuransi kendaraan, dihitung per tahun polis lalu dijumlahkan."""

from .tiers import lookup_tier, lookup_exact


def _age_loading(age, loading_table):
    """Loading usia kendaraan. Di bawah ambang tabel = 0; di atas tabel = error."""
    if not loading_table:
        return 0.0
    if age < min(loading_table):
        return 0.0
    if age > max(loading_table):
        raise ValueError(
            f"Umur kendaraan {age} tahun di luar tabel loading "
            f"(tabel mencakup {min(loading_table)}-{max(loading_table)} tahun)"
        )
    return loading_table[age]


def insurance_premium(otr, vehicle_year, tenor_months, region, ins_cfg, as_of_year):
    """Total premi asuransi untuk seluruh tenor pembiayaan.

    Nilai pertanggungan, jenis coverage, dan umur kendaraan berubah tiap tahun,
    jadi premi dihitung per tahun polis lalu dijumlahkan.

    Umur kendaraan di tahun polis ke-n = (as_of_year - vehicle_year) + n.
    Konvensi +1 ini diturunkan dari rekonsiliasi terhadap nilai Excel dan tidak
    terdokumentasi di workbook aslinya.
    """
    if otr <= 0:
        raise ValueError(f"OTR harus positif, dapat {otr}")
    if tenor_months <= 0 or tenor_months % 12 != 0:
        raise ValueError(
            f"Tenor {tenor_months} harus positif dan kelipatan 12 bulan; "
            f"tenor pecahan tahun belum didukung"
        )
    if as_of_year < vehicle_year:
        raise ValueError(
            f"Tahun kendaraan {vehicle_year} ada di masa depan terhadap as_of_year {as_of_year}"
        )

    years = tenor_months // 12
    max_years = len(ins_cfg["depreciation"])
    if years > max_years:
        raise ValueError(
            f"Tenor {tenor_months} bulan ({years} tahun) melebihi tabel depresiasi "
            f"yang hanya mencakup {max_years} tahun"
        )

    known_regions = sorted({r for _, r in ins_cfg["rates"]})
    if region not in known_regions:
        raise ValueError(f"Region {region} tidak dikenal. Tersedia: {known_regions}")

    base_age = as_of_year - vehicle_year
    limits = ins_cfg["sum_insured_limits"]

    total = 0.0
    for year in range(1, years + 1):
        sum_insured = otr * ins_cfg["depreciation"][year - 1]
        coverage = ins_cfg["coverage"][year - 1]

        rates = lookup_exact(ins_cfg["rates"], (coverage, region))
        rate = lookup_tier(sum_insured, list(zip(limits, rates)), above=rates[-1])

        if coverage in ins_cfg["loading_applies_to"]:
            loading = _age_loading(base_age + year, ins_cfg["loading_by_age"])
        else:
            loading = 0.0

        total += sum_insured * rate * (1 + loading)

    return total
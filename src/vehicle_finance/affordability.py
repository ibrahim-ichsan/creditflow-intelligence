"""Kemampuan bayar: tabel aturan DBR dan pengecekan kapasitas."""


def rule_matches(conditions, profile):
    """True kalau SEMUA kondisi satu aturan terpenuhi oleh profile.

    Dua jenis kondisi:
      "payroll": False          -> kesamaan,  profile["payroll"] == False
      "min_salary": 10_000_000  -> ambang,    profile["salary"] >= 10_000_000

    Field yang tidak ada di profile -> ValueError yang menyebut nama field-nya.
    """
    for key, want in conditions.items():
        is_minimum = key.startswith("min_")
        field = key[4:] if is_minimum else key
        if field not in profile:
            raise ValueError(f"field {field!r} tidak ada di profile")

        actual = profile[field]
        if (is_minimum and actual < want) or (not is_minimum and actual != want):
            return False

    return True


def dbr_ratio(profile, rules):
    """Rasio DBR dari aturan PERTAMA yang cocok.

    Tidak ada yang cocok -> ValueError. Itu bug di tabel atau di profile,
    bukan alasan untuk diam-diam memakai nilai default.
    """
    for conditions, ratio in rules:
        if rule_matches(conditions, profile):
            return ratio

    raise ValueError(f"tidak ada aturan DBR yang cocok untuk profile {profile!r}")


def dbr_check(dbr_app, rules, capacity_ratio=None, disclaimer=None):
    """Cek kemampuan bayar terhadap kapasitas.

    dbr_app : universe + flag segmen yang dibutuhkan aturan, plus
              salary, incentive, new_installment, other_installments
    capacity_ratio : None -> pakai rasio hasil tabel aturan.
                     Livin mengoper CAPACITY_RATIO_OVERRIDE (0.65).

    Mengembalikan dict: dbr_ratio, capacity_ratio, capacity,
    capacity_with_incentive, total_installment, shortfall, must_repay,
    passed, disclaimer.
    """
    salary = dbr_app["salary"]
    if salary <= 0:
        raise ValueError("salary harus lebih besar dari 0")

    incentive = dbr_app["incentive"]
    new_installment = dbr_app["new_installment"]
    other_installments = dbr_app["other_installments"]
    for field, value in (
        ("incentive", incentive),
        ("new_installment", new_installment),
        ("other_installments", other_installments),
    ):
        if value is None:
            raise ValueError(f"{field} tidak boleh None; pakai 0 kalau tidak ada")
        if value < 0:
            raise ValueError(f"{field} tidak boleh negatif")

    ratio = dbr_ratio(dbr_app, rules)
    effective_ratio = ratio if capacity_ratio is None else capacity_ratio
    capacity = salary * effective_ratio
    capacity_with_incentive = capacity + incentive
    total_installment = new_installment + other_installments
    shortfall = max(0, total_installment - capacity_with_incentive)
    must_repay = min(shortfall, other_installments)
    passed = total_installment <= capacity_with_incentive

    return {
        "dbr_ratio": ratio,
        "capacity_ratio": effective_ratio,
        "capacity": capacity,
        "capacity_with_incentive": capacity_with_incentive,
        "total_installment": total_installment,
        "shortfall": shortfall,
        "must_repay": must_repay,
        "passed": passed,
        "disclaimer": None if passed else disclaimer,
    }

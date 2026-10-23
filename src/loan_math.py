from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def to_cents(value):
    """Ubah angka jadi Decimal, dibulatkan ke sen (round half up)."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def monthly_installment(principal, annual_rate, tenor_months):
    """Cicilan bulanan anuitas (effective rate).

    Rumus: P * r * (1 + r)**n / ((1 + r)**n - 1)
    dengan r = annual_rate / 12, n = tenor_months
    annual_rate ditulis desimal: 8% -> 0.08
    """
    r = annual_rate / 12
    if r == 0:
        return principal / tenor_months
    return principal * r * (1 + r) ** tenor_months / ((1 + r) ** tenor_months - 1)


def amortization_schedule(principal, annual_rate, tenor_months):
    """installment schedule (without rounding)"""
    installment = monthly_installment(principal, annual_rate, tenor_months)
    r = annual_rate / 12

    rows = []
    balance = principal

    for month in range(1, tenor_months + 1):
      #   bunga bulan ini      = sisa pokok * r
        interest = balance * r
      #   pokok dibayar        = cicilan - bunga
        principal_paid = installment - interest
      #   sisa pokok baru      = sisa pokok - pokok dibayar
        balance = balance - principal_paid
      #   simpan sebagai dict ke list
        rows.append({
            "month": month,
            "installment": installment,
            "interest": interest,
            "principal_paid": principal_paid,
            "balance": balance,
        })

    return rows

def amortization_schedule_rounded(principal, annual_rate, tenor_months):
    """Jadwal angsuran dengan pembulatan ke sen.
    Bulan terakhir menyerap selisih pembulatan, saldo akhir persis 0.00.
    """
    installment = to_cents(monthly_installment(principal, annual_rate, tenor_months))
    r = Decimal(str(annual_rate)) / Decimal("12")
    balance = to_cents(principal)
    rows = []

    for month in range(1, tenor_months + 1):
        interest = to_cents(balance * r)

        if month == tenor_months:
            # bulan terakhir: lunasi semua sisa pokok
            principal_paid = balance
            payment = principal_paid + interest
        else:
            principal_paid = installment - interest
            payment = installment

        balance = balance - principal_paid
        rows.append({
            "month": month,
            "installment": payment,
            "interest": interest,
            "principal_paid": principal_paid,
            "balance": balance,
        })

    return rows
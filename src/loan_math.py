def monthly_installment(principal, annual_rate, tenor_months):
    """Cicilan bulanan anuitas (effective rate).

    Rumus: P * r * (1 + r)**n / ((1 + r)**n - 1)
    dengan r = annual_rate / 12, n = tenor_months
    annual_rate ditulis desimal: 8% -> 0.08
    """
    # TODO 1: hitung r
    r = annual_rate / 12
    # TODO 2: kalau r == 0, rumus di atas bagi nol. Cicilannya berapa? (pikirin logikanya)
    if r == 0:
        return principal / tenor_months
    # TODO 3: return hasil rumus
    return principal * r * (1 + r) ** tenor_months / ((1 + r) ** tenor_months - 1)


def amortization_schedule(principal, annual_rate, tenor_months):
    """...docstring..."""
    # TODO 4: panggil monthly_installment untuk dapat cicilan
    installment = monthly_installment(principal, annual_rate, tenor_months)
    r = annual_rate / 12

    # TODO 5: siapkan list kosong + sisa pokok awal = principal
    rows = []
    balance = principal

    # TODO 6: loop dari bulan 1 sampai tenor_months
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

    # TODO 7: return list-nya
    return rows

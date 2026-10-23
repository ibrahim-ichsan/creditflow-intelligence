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
    """Return list of dict, satu dict per bulan, berisi:
    month, installment, interest, principal_paid, balance
    """
    # TODO 4: panggil monthly_installment untuk dapat cicilan
    # TODO 5: siapkan list kosong + sisa pokok awal = principal
    # TODO 6: loop dari bulan 1 sampai tenor_months:
    #   bunga bulan ini      = sisa pokok * r
    #   pokok dibayar        = cicilan - bunga
    #   sisa pokok baru      = sisa pokok - pokok dibayar
    #   simpan sebagai dict ke list
    # TODO 7: return list-nya
    pass
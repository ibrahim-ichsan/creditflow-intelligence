"""Generic lookup helpers that replace Excel's nested IF, VLOOKUP and XLOOKUP."""


def lookup_tier(value, tiers, above):
    """Return the result of the first tier whose upper limit is >= value.

    tiers: list of (upper_limit, result), sorted ascending by upper_limit.
    above: result returned when value exceeds every upper limit.
    Raises ValueError if value is None or tiers are not sorted ascending.
    """
    # TODO 1: kalau value None -> raise ValueError("value is required")
    if value is None:
        raise ValueError("value is required")
    # TODO 2: kalau tiers tidak urut naik -> raise ValueError
    if tiers != sorted(tiers, key=lambda x: x[0]):
        raise ValueError("tiers must be sorted ascending by upper_limit")
    # TODO 3: loop tiers; kalau value <= upper_limit -> return result-nya
    for upper_limit, result in tiers:
        if value <= upper_limit:
            return result
    # TODO 4: lolos semua tier -> return above
    return above


def lookup_exact(table, key):
    """Exact lookup, e.g. rate by tenor. Fails loudly instead of returning 'Not found'."""
    # TODO: kalau key ada di table -> return nilainya
    #       kalau tidak ada -> raise ValueError, dengan pesan yang menyebut key yang dicari
    #       dan daftar key yang tersedia
    if key in table:
        return table[key]
    raise ValueError(f"key {key} not found in table. Available keys: {list(table.keys())}")
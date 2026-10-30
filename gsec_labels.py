import pandas as pd


def spreads_from_table(table):
    return pd.DataFrame({
        "2s5s": (table[5] - table[2]) * 100,
        "2s10s": (table[10] - table[2]) * 100,
        "5s10s": (table[10] - table[5]) * 100,
        "10s30s": (table[30] - table[10]) * 100,
    })


def classify(change_bps, threshold):
    """Steepening if the spread widened by at least the threshold,
    flattening if it narrowed by at least the threshold, else little changed."""
    if abs(change_bps) < threshold:
        return "little changed"
    return "steepening" if change_bps > 0 else "flattening"


def level_label(spread_value):
    return "inverted" if spread_value < 0 else "upward sloping"


def noise_floor(spreads, n_days=10):
    """Median absolute day-to-day change over the last n_days consecutive rows."""
    return spreads.tail(n_days).diff().abs().median()


def label_period(spreads, start, end, threshold):
    rows = []
    for name in spreads.columns:
        change = spreads.loc[end, name] - spreads.loc[start, name]
        rows.append({
            "spread": name,
            "start": round(spreads.loc[start, name], 1),
            "end": round(spreads.loc[end, name], 1),
            "change_bps": round(change, 1),
            "label": classify(change, threshold[name]),
            "shape_now": level_label(spreads.loc[end, name]),
        })
    return pd.DataFrame(rows)

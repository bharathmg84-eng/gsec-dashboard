import pandas as pd
from pandas.tseries.offsets import BDay


def changes_bps(table, offset, tol_days=0):
    """Yield change in bps versus the date one 'offset' earlier.
    If no row exists within tol_days of that target date, the result is NaN."""
    out = pd.DataFrame(index=table.index, columns=table.columns, dtype=float)
    idx = table.index
    for d in idx:
        target = d - offset
        pos = idx.get_indexer([target], method="nearest")[0]
        base = idx[pos]
        if base < d and abs((base - target).days) <= tol_days:
            out.loc[d] = (table.loc[d] - table.loc[base]) * 100
    return out


def all_changes(table):
    daily = changes_bps(table, BDay(1), 0)
    weekly = changes_bps(table, pd.Timedelta(days=7), 1)
    monthly = changes_bps(table, pd.DateOffset(months=1), 3)
    return daily, weekly, monthly

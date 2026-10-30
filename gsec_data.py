import glob
import numpy as np
import pandas as pd

TENORS = [1, 2, 3, 5, 7, 10, 15, 20, 30]


def load_fbil(path):
    raw = pd.read_excel(path, header=None)
    val_date = pd.to_datetime(raw.iloc[2, 2], format="%d-%b-%Y")
    hdr = raw.index[raw[0] == "ISIN"][0]
    df = raw.iloc[hdr + 1:, :8].copy()
    df.columns = ["isin", "coupon", "maturity", "price", "ytm", "remark1", "remark2", "remark3"]
    df = df[df["isin"].astype(str).str.startswith("IN")]
    df["maturity"] = pd.to_datetime(df["maturity"], errors="coerce")
    for col in ["coupon", "price", "ytm"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["maturity", "price", "ytm"])
    df = df[~df["remark1"].isin(["FRB", "IIB"])]
    df["years"] = (df["maturity"] - val_date).dt.days / 365.25
    return val_date, df


def curve_at_tenors(df, tenors=TENORS):
    d = df[df["years"] > 0].sort_values("years")
    out = {}
    for t in tenors:
        if d["years"].min() <= t <= d["years"].max():
            out[t] = float(np.interp(t, d["years"], d["ytm"]))
        else:
            out[t] = np.nan
    return out


def build_table(folder="data"):
    rows = {}
    for f in sorted(glob.glob(f"{folder}/*.xlsx")):
        d, df = load_fbil(f)
        rows[d] = curve_at_tenors(df)
    table = pd.DataFrame(rows).T.sort_index()
    table.index.name = "date"
    return table

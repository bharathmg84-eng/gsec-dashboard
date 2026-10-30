from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from gsec_data import build_table
from gsec_changes import all_changes
from gsec_labels import spreads_from_table, noise_floor, label_period

st.set_page_config(page_title="Indian G-Sec yield dashboard", layout="wide")


@st.cache_data
def load_all():
    table = build_table(str(Path(__file__).parent / "data"))
    daily, weekly, monthly = all_changes(table)
    spreads = spreads_from_table(table)
    return table, daily, weekly, monthly, spreads


table, daily, weekly, monthly, spreads = load_all()
thr = noise_floor(spreads, 10)


def fmt(d):
    return d.strftime("%d %b %Y")


st.title("Indian G-Sec yield dashboard")
st.caption("Yields are interpolated from individual G-Sec YTMs in FBIL's daily price files. "
           "Dates are sampled, not every business day.")

dates = list(table.index)
selected = st.sidebar.selectbox("Date", dates, index=len(dates) - 1, format_func=fmt)
earlier = [d for d in dates if d < selected]
if not earlier:
    st.warning("Pick a later date: there is no earlier date to compare with.")
    st.stop()
target = selected - pd.Timedelta(days=28)
default = min(range(len(earlier)), key=lambda i: abs((earlier[i] - target).days))
compare = st.sidebar.selectbox("Compare with", earlier, index=default, format_func=fmt)

c1, c2, c3 = st.columns(3)
y_now, y_then = table.loc[selected, 10], table.loc[compare, 10]
c1.metric("10Y yield", f"{y_now:.2f}%",
          f"{(y_now - y_then) * 100:+.1f} bps vs {fmt(compare)}", delta_color="off")
c2.metric("2s10s spread", f"{spreads.loc[selected, '2s10s']:.1f} bps",
          f"{spreads.loc[selected, '2s10s'] - spreads.loc[compare, '2s10s']:+.1f} bps", delta_color="off")
c3.metric("5s10s spread", f"{spreads.loc[selected, '5s10s']:.1f} bps",
          f"{spreads.loc[selected, '5s10s'] - spreads.loc[compare, '5s10s']:+.1f} bps", delta_color="off")

left, right = st.columns(2)

with left:
    st.subheader("Yield curve")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(table.columns, table.loc[compare], marker="o", label=fmt(compare))
    ax.plot(table.columns, table.loc[selected], marker="o", color="black",
            linewidth=2.2, label=fmt(selected))
    ax.set_xlabel("Tenor (years)")
    ax.set_ylabel("Yield (%)")
    ax.legend()
    st.pyplot(fig)

with right:
    st.subheader("10Y yield history (sampled dates)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(table.index, table[10], marker="o")
    ax2.axvline(selected, color="black", linestyle="--", linewidth=1)
    ax2.set_ylabel("10Y yield (%)")
    fig2.autofmt_xdate()
    st.pyplot(fig2)

st.subheader(f"Yield changes to {fmt(selected)} (bps)")
changes = pd.DataFrame({
    "daily": daily.loc[selected],
    "weekly": weekly.loc[selected],
    "monthly": monthly.loc[selected],
})
changes.index.name = "tenor (years)"
st.dataframe(changes, column_config={
    c: st.column_config.NumberColumn(format="%.1f") for c in changes.columns})
st.caption("None means no earlier date was close enough to compare with. Daily needs the previous "
           "business day, weekly a date within 1 day of 7 days earlier, monthly within 3 days of one month earlier.")

st.subheader(f"Curve shape: {fmt(compare)} to {fmt(selected)}")
st.dataframe(
    label_period(spreads, compare, selected, thr),
    hide_index=True,
    column_config={
        "start": st.column_config.NumberColumn(format="%.1f"),
        "end": st.column_config.NumberColumn(format="%.1f"),
        "change_bps": st.column_config.NumberColumn(format="%+.1f"),
    },
)
st.caption("Steepening or flattening needs a spread change at least as large as the typical one-day move "
           "over the last 10 business days: "
           + ", ".join(f"{k} {v:.1f} bps" for k, v in thr.items()) + ".")

with st.expander("Data and limitations"):
    st.markdown(
        "- Source: FBIL daily G-Sec price files, downloaded by hand. FBIL does not authorise commercial use "
        "without written permission, so this is a personal, non-commercial study.\n"
        "- Floating-rate bonds are excluded.\n"
        "- Yields at fixed tenors come from straight-line interpolation between neighbouring bonds, "
        "not from FBIL's own fitted curve.\n"
        "- The 1Y point is noisy and is not used in the spread labels.\n"
        "- Dates are sampled: daily for the last 10 business days, weekly and about monthly before that.\n"
        "- The label threshold comes from only 10 days of data, so it is a rough rule."
    )

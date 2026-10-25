# Data sources

- Source: FBIL (Financial Benchmarks India Pvt. Ltd.), G-Sec tab under Fixed Income Securities. File name: "FBIL GOI Prices including Par Yield, Special and Note on FRB and IIB"
- Link: https://www.fbil.org.in/
- File format: .xlsx, one file per valuation date. Each row is one government security with ISIN, coupon, maturity, price and YTM (semi-annual).
- Files used so far: 2026-09-09, 2026-10-09, 2026-10-16 (more dates added on Day 2)
- Downloaded on: 25 Oct 2026
- Latest date available when downloaded: 16 Oct 2026 (the site publishes with a delay)

## Cleaning
- Floating-rate bonds (remark "FRB") are excluded, leaving 119 fixed-rate bonds per file. Their yields are not comparable with fixed-rate yields.
- Rows tagged "Input Point", "YC", "Proxy" and "T" are kept. Their meaning is still to be checked against FBIL's methodology document.

## Curve type
- YTM of individual fixed-rate G-Secs, to be interpolated to fixed tenors (for example 1Y, 5Y, 10Y). This is not FBIL's own published par yield curve.

## Terms
- FBIL provides its data as-is, without warranty, and does not authorise commercial use without written permission.
- This project uses the data for personal, non-commercial study. Raw FBIL files are not republished here (the data/ folder is git-ignored). To reproduce, download them from the FBIL site.

## Limitations
- Dates are sampled (daily for recent days, weekly, month-end), not every business day.
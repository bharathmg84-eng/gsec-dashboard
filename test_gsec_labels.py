import pandas as pd
from gsec_labels import classify, level_label, spreads_from_table, noise_floor, label_period


def test_spreads_from_table():
    table = pd.DataFrame(
        [[6.0, 6.5, 7.0, 7.5], [6.0, 6.4, 7.2, 7.4]],
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
        columns=[2, 5, 10, 30],
    )
    s = spreads_from_table(table)
    assert abs(s.loc["2026-01-01", "2s5s"] - 50) < 1e-9
    assert abs(s.loc["2026-01-01", "2s10s"] - 100) < 1e-9
    assert abs(s.loc["2026-01-02", "5s10s"] - 80) < 1e-9
    assert abs(s.loc["2026-01-02", "10s30s"] - 20) < 1e-9


def test_classify_directions():
    assert classify(5, 2) == "steepening"
    assert classify(-5, 2) == "flattening"
    assert classify(1, 2) == "little changed"


def test_classify_boundary():
    assert classify(2, 2) == "steepening"
    assert classify(-2, 2) == "flattening"
    assert classify(1.99, 2) == "little changed"


def test_inversion_label():
    assert level_label(-1) == "inverted"
    assert level_label(0.5) == "upward sloping"
    assert level_label(0) == "upward sloping"


def test_noise_floor():
    s = pd.DataFrame({"x": [0, 2, 1, 4]})
    assert noise_floor(s, n_days=4)["x"] == 2


def test_label_period():
    s = pd.DataFrame({"2s10s": [100.0, 120.0]},
                     index=pd.to_datetime(["2026-01-01", "2026-01-02"]))
    out = label_period(s, "2026-01-01", "2026-01-02", pd.Series({"2s10s": 5}))
    assert out.loc[0, "change_bps"] == 20.0
    assert out.loc[0, "label"] == "steepening"
    assert out.loc[0, "shape_now"] == "upward sloping"

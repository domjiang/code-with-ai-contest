import pandas as pd
import numpy as np


def test_data_loading():
    df = pd.read_csv("data/signal_samples.csv")
    assert not df.empty
    expected_columns = [
        "Latitude", "Longitude", "CellID", "Band",
        "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps",
    ]
    for col in expected_columns:
        assert col in df.columns, f"缺少列: {col}"


def test_rsrp_color():
    from utils import rsrp_color
    assert rsrp_color(-80) == [0, 200, 0, 180], "强信号应为绿色"
    assert rsrp_color(-115) == [200, 0, 0, 180], "弱信号应为红色"
    color_mid = rsrp_color(-100)
    assert len(color_mid) == 4
    assert all(0 <= c <= 255 for c in color_mid[:3])


def test_filter_logic():
    df = pd.DataFrame({
        "Band": ["n41", "n78", "n28"],
        "RSRP_dBm": [-95, -85, -115],
        "TerminalType": ["Smartphone", "CPE", "IoT"],
    })
    mask = (
        df["Band"].isin(["n41", "n78"])
        & df["RSRP_dBm"].between(-110, -80)
        & df["TerminalType"].isin(["Smartphone", "CPE"])
    )
    result = df[mask]
    assert len(result) == 2
    assert all(result["Band"].isin(["n41", "n78"]))


def test_rgba_to_hex():
    from utils import rgba_to_hex
    assert rgba_to_hex([0, 200, 0, 180]) == "#00c800b4"
    assert rgba_to_hex([200, 0, 0, 180]) == "#c80000b4"
    assert rgba_to_hex([100, 100, 0, 180]) == "#646400b4"


def test_approx_district():
    from utils import approx_district
    dist = approx_district(31.23, 121.48)
    assert isinstance(dist, str) and len(dist) > 0


def test_band_distribution():
    df = pd.read_csv("data/signal_samples.csv")
    counts = df["Band"].value_counts()
    assert "n28" in counts.index
    assert "n41" in counts.index
    assert "n78" in counts.index
    assert counts.sum() == len(df)


def test_terminal_type_distribution():
    df = pd.read_csv("data/signal_samples.csv")
    counts = df["TerminalType"].value_counts()
    expected_types = {"Smartphone", "CPE", "IoT"}
    assert expected_types.issubset(set(counts.index))
    assert counts.sum() == len(df)

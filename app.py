import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import os
import base64
from utils import rsrp_color, approx_district

st.set_page_config(page_title="5G 信号可视化看板", layout="wide")
st.title("📡 5G 信号可视化看板")
st.markdown("基于 **上海 5G 路测数据** 的交互式可视化看板 — 使用左侧筛选器实时过滤数据")


def color_swatch(rgba):
    """将 RGBA 颜色数组转为 ImageColumn 可用的 data URL。"""
    r, g, b, a = rgba
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" rx="3" fill="rgba({r},{g},{b},{a/255})"/></svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@st.cache_data(show_spinner="正在加载数据...")
def load_data():
    df = pd.read_csv("data/signal_samples.csv")

    # Try loading cached district data
    cache_file = "data/districts_cache.csv"
    if os.path.exists(cache_file):
        cache = pd.read_csv(cache_file)
        if len(cache) == len(df) and "District" in cache.columns:
            df["District"] = cache["District"]
            return df

    # Fallback: approximate by nearest district center
    df["District"] = df.apply(
        lambda row: approx_district(row["Latitude"], row["Longitude"]), axis=1
    )
    return df


df = load_data()

# ── Sidebar filters ──
st.sidebar.header("筛选条件")

selected_bands = st.sidebar.multiselect(
    "频段 (Band)",
    options=sorted(df["Band"].unique()),
    default=sorted(df["Band"].unique()),
)

rsrp_min = float(df["RSRP_dBm"].min())
rsrp_max = float(df["RSRP_dBm"].max())
rsrp_range = st.sidebar.slider(
    "信号强度范围 (RSRP dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(rsrp_min, rsrp_max),
)

selected_terminals = st.sidebar.multiselect(
    "终端类型",
    options=sorted(df["TerminalType"].unique()),
    default=sorted(df["TerminalType"].unique()),
)

selected_districts = st.sidebar.multiselect(
    "行政区",
    options=sorted(df["District"].unique()),
    default=sorted(df["District"].unique()),
)

map_3d = st.sidebar.checkbox("3D 地图模式 (柱高度 = 下载速率)", value=False)

# ── Filter data ──
mask = (
    df["Band"].isin(selected_bands)
    & df["RSRP_dBm"].between(rsrp_range[0], rsrp_range[1])
    & df["TerminalType"].isin(selected_terminals)
    & df["District"].isin(selected_districts)
)
filtered = df[mask].copy()

# ── Color by RSRP (for pydeck) ──
filtered["color"] = filtered["RSRP_dBm"].apply(rsrp_color)

# ── Map ──
st.subheader("🗺️ 信号覆盖地图")

if not filtered.empty:
    # Build pydeck layer (adds "height" for 3D mode internally)
    if map_3d:
        filtered["height"] = filtered["Download_Mbps"] * 2
        layer = pdk.Layer(
            "ColumnLayer",
            data=filtered,
            get_position=["Longitude", "Latitude"],
            get_elevation="height",
            elevation_scale=1,
            radius=50,
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        )
        pitch = 45
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position=["Longitude", "Latitude"],
            get_fill_color="color",
            get_radius=80,
            pickable=True,
            auto_highlight=True,
        )
        pitch = 0

    view_state = pdk.ViewState(
        latitude=filtered["Latitude"].mean(),
        longitude=filtered["Longitude"].mean(),
        zoom=11,
        pitch=pitch,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "text": "RSRP: {RSRP_dBm} dBm\nBand: {Band}\nSINR: {SINR_dB} dB\n速率: {Download_Mbps} Mbps\n终端: {TerminalType}\n区: {District}"
        },
    )
    st.pydeck_chart(deck)
else:
    st.warning("当前筛选条件下没有数据，请调整筛选条件。")

# ── Charts ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("各频段基站数量")
    band_counts = filtered["Band"].value_counts().reset_index()
    band_counts.columns = ["Band", "Count"]
    fig_band = px.bar(
        band_counts,
        x="Band",
        y="Count",
        color="Band",
        text_auto=True,
        color_discrete_map={"n28": "#636efa", "n41": "#ef553b", "n78": "#00cc96"},
    )
    fig_band.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_band, width='stretch')

with col2:
    st.subheader("终端类型分布")
    term_counts = filtered["TerminalType"].value_counts().reset_index()
    term_counts.columns = ["TerminalType", "Count"]
    fig_term = px.pie(term_counts, names="TerminalType", values="Count", hole=0.4)
    fig_term.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_term, width='stretch')

# ── Data preview ──
with st.expander("📊 数据预览"):
    col_count = st.columns(3)
    col_count[0].metric("总样本数", len(filtered))
    col_count[1].metric("平均 RSRP", f"{filtered['RSRP_dBm'].mean():.1f} dBm")
    col_count[2].metric("平均下载速率", f"{filtered['Download_Mbps'].mean():.1f} Mbps")

    # Prepare display columns — color/height are internal rendering params only
    filtered["swatch"] = filtered["color"].apply(color_swatch)
    display_cols = [
        "Latitude", "Longitude", "District",
        "CellID", "Band", "RSRP_dBm", "SINR_dB",
        "TerminalType", "Download_Mbps", "swatch",
    ]
    display_df = filtered[display_cols].copy()
    display_df.rename(
        columns={
            "swatch": "信号强度",
            "District": "行政区",
            "Latitude": "纬度",
            "Longitude": "经度",
            "CellID": "小区ID",
            "Band": "频段",
            "RSRP_dBm": "RSRP (dBm)",
            "SINR_dB": "SINR (dB)",
            "TerminalType": "终端类型",
            "Download_Mbps": "下载速率 (Mbps)",
        },
        inplace=True,
    )

    st.dataframe(
        display_df,
        column_config={
            "信号强度": st.column_config.ImageColumn("信号强度", help="RSRP 颜色映射"),
        },
        width='stretch',
        hide_index=True,
    )

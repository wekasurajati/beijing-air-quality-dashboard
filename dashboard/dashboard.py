import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from pathlib import Path


# KONFIGURASI HALAMAN

st.set_page_config(
    page_title="Pantauan Kualitas Udara Beijing",
    layout="wide",
    initial_sidebar_state="expanded",
)


# IKON 

ICONS = {
    "gauge": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a9 9 0 0 0-9 9c0 2.1.72 4.03 1.93 5.56"/>
        <path d="M21 12a9 9 0 0 0-3.4-7.04"/><path d="M8.5 17.5 12 12l6-4"/><circle cx="12" cy="12" r="1.3" fill="currentColor" stroke="none"/></svg>""",
    "smoke": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="10" width="7" height="11"/>
        <path d="M6.5 10V6a2.5 2.5 0 0 1 5 0"/><path d="M14 21c2-1 4-3 4-6s-2-4-2-6 1-3 1-3"/>
        <path d="M19 21c1.4-1 3-2.6 3-5"/></svg>""",
    "station": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v6"/><path d="M8.5 6.5a5 5 0 0 1 7 0"/>
        <path d="M5.5 3.5a9 9 0 0 1 13 0"/><rect x="7" y="10" width="10" height="11" rx="1"/>
        <path d="M10 21v-5h4v5"/></svg>""",
    "calendar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="1.5"/>
        <path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/></svg>""",
    "map": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21Z"/>
        <circle cx="12" cy="9.5" r="2.4"/></svg>""",
    "layers": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 9l10 6 10-6-10-6Z"/>
        <path d="m2 15 10 6 10-6"/><path d="M2 12l10 6 10-6"/></svg>""",
    "trend": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M3 17 9 11l4 4 8-8"/><path d="M16 7h5v5"/></svg>""",
    "wind": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h11a2.5 2.5 0 1 0-2.4-3.2"/>
        <path d="M3 13h15a2.5 2.5 0 1 1-2.4 3.2"/><path d="M3 18h8a2 2 0 1 1-1.8 2.8"/></svg>""",
}


def icon(name, size=18):
    return f'<span class="icon-box" style="width:{size}px;height:{size}px">{ICONS[name]}</span>'



# VISUAL 

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    html, body, [class*="css"]  { font-family: 'IBM Plex Sans', sans-serif; }

    :root{
        --bg-0:#0d1117;
        --bg-1:#141a22;
        --bg-2:#1b232d;
        --line:#28323e;
        --text-0:#e7edf3;
        --text-1:#98a7b6;
        --accent:#3d8bfd;
        --good:#3fb27f;
        --moderate:#e0b23e;
        --unhealthy-s:#e08a3e;
        --unhealthy:#d9534f;
        --very-unhealthy:#9a4fd9;
        --hazard:#6b1f2a;
    }


       .stApp {
        color: var(--text-0);
        background-color: var(--bg-0);
        background-image: 
            radial-gradient(ellipse 75% 45% at 12% -8%, rgba(110, 168, 255, 0.30), transparent 70%), 
            radial-gradient(ellipse 65% 42% at 88% -4%, rgba(157, 91, 237, 0.35), transparent 60%), 
            radial-gradient(ellipse 55% 40% at 50% 105%, rgba(255, 105, 180, 0.15), transparent 60%);
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    section[data-testid="stSidebar"] { background-color: var(--bg-1); border-right: 1px solid var(--line); }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .icon-box { display:inline-flex; vertical-align:middle; }
    .icon-box svg { width:100%; height:100%; }

    .app-header{
        display:flex; flex-direction:column; align-items:center; text-align:center; gap:2px;
        padding: 30px 22px 24px 22px; margin-bottom: 6px;
        background: linear-gradient(180deg, var(--bg-1), var(--bg-0));
        border: 1px solid var(--line); border-radius: 10px;
    }
    .app-header .icon-box{ color: var(--accent); width:34px; height:34px; margin-bottom:8px; }
    .app-header h1{
        font-size: 2.1rem; margin:0; letter-spacing:.2px; color: var(--text-0); font-weight:700;
    }
    .app-header .app-subtitle{ margin:6px 0 0 0; color: var(--text-1); font-size:.9rem; }
    .app-header .app-author{
        margin-top:14px; color: var(--text-1); font-size:.76rem;
        font-family:'IBM Plex Mono', monospace; letter-spacing:.3px;
    }

    .section-title{
        display:flex; align-items:center; gap:8px; margin: 26px 0 10px 0;
        color: var(--text-0); font-weight:600; font-size:1.02rem;
        border-bottom: 1px solid var(--line); padding-bottom:8px;
    }
    .section-title .icon-box{ color: var(--accent); }

    .kpi-card{
        background: var(--bg-1); border: 1px solid var(--line); border-radius: 10px;
        padding: 14px 16px; height: 148px;
        display:flex; flex-direction:column; justify-content:space-between;
    }
    .kpi-card .kpi-top{ display:flex; align-items:flex-start; justify-content:space-between; gap:8px; color: var(--text-1); min-height:32px; }
    .kpi-card .icon-box{ color: var(--accent); flex-shrink:0; }
    .kpi-card .kpi-label{ font-size:.74rem; text-transform:uppercase; letter-spacing:.6px; color: var(--text-1); line-height:1.3; }
    .kpi-card .kpi-value{ font-family:'IBM Plex Mono', monospace; font-size:1.65rem; font-weight:600; color: var(--text-0); }
    .kpi-card .kpi-sub{ font-size:.72rem; color: var(--text-1); }

    .badge{
        display:inline-block; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:600;
        font-family:'IBM Plex Mono', monospace;
    }
    .badge-good{ background:rgba(63,178,127,.15); color:var(--good); border:1px solid rgba(63,178,127,.4);}
    .badge-moderate{ background:rgba(224,178,62,.15); color:var(--moderate); border:1px solid rgba(224,178,62,.4);}
    .badge-unhealthy-s{ background:rgba(224,138,62,.15); color:var(--unhealthy-s); border:1px solid rgba(224,138,62,.4);}
    .badge-unhealthy{ background:rgba(217,83,79,.15); color:var(--unhealthy); border:1px solid rgba(217,83,79,.4);}

    .note-box{
        background: var(--bg-1); border: 1px solid var(--line); border-left: 3px solid var(--accent);
        border-radius: 6px; padding: 10px 14px; color: var(--text-1); font-size:.85rem; margin-top:8px;
    }

    div[data-testid="stMetric"]{ background: var(--bg-1); border:1px solid var(--line); border-radius:10px; padding:10px 14px; }

    footer.app-footer{ color: var(--text-1); font-size:.75rem; text-align:center; padding: 26px 0 6px 0; border-top:1px solid var(--line); margin-top:30px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# DATA

BASE_DIR = Path(__file__).resolve().parent

STATION_COORDS = {
    "Dongsi": (39.929, 116.417),
    "Tiantan": (39.886, 116.407),
    "Guanyuan": (39.929, 116.339),
    "Wanshouxigong": (39.878, 116.352),
    "Aotizhongxin": (39.982, 116.397),
    "Nongzhanguan": (39.937, 116.461),
    "Wanliu": (39.987, 116.287),
    "Gucheng": (39.914, 116.184),
    "Shunyi": (40.127, 116.655),
    "Changping": (40.217, 116.230),
    "Huairou": (40.328, 116.628),
    "Dingling": (40.292, 116.220),
}

CATEGORY_ORDER = [
    "Baik", "Sedang", "Tidak Sehat bagi Kelompok Sensitif",
    "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya",
]
CATEGORY_COLOR = {
    "Baik": "#3fb27f",
    "Sedang": "#e0b23e",
    "Tidak Sehat bagi Kelompok Sensitif": "#e08a3e",
    "Tidak Sehat": "#d9534f",
    "Sangat Tidak Sehat": "#9a4fd9",
    "Berbahaya": "#6b1f2a",
}
MONTH_LABEL = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["datetime"])
    df["kategori_pm25"] = pd.Categorical(df["kategori_pm25"], categories=CATEGORY_ORDER, ordered=True)
    return df


def marker_color(value: float) -> str:
    if value >= 85:
        return "#d9534f"
    elif value >= 75:
        return "#e08a3e"
    return "#3fb27f"


def category_badge(cat: str) -> str:
    mapping = {
        "Baik": "badge-good",
        "Sedang": "badge-moderate",
        "Tidak Sehat bagi Kelompok Sensitif": "badge-unhealthy-s",
    }
    cls = mapping.get(cat, "badge-unhealthy")
    return f'<span class="badge {cls}">{cat}</span>'


data = load_data()


# SIDEBAR

with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;color:#e7edf3;font-weight:600;font-size:1rem;">'
        f'{icon("layers", 20)} Filter Data</div>',
        unsafe_allow_html=True,
    )
    st.caption("Sesuaikan cakupan data yang ditampilkan pada seluruh dashboard.")

    all_stations = sorted(data["station"].unique())
    selected_stations = st.multiselect(
        "Stasiun pemantauan", options=all_stations, default=all_stations
    )

    min_date, max_date = data["datetime"].min().date(), data["datetime"].max().date()
    date_range = st.date_input(
        "Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    pollutant = st.selectbox(
        "Polutan untuk peta & KPI", options=["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"], index=0
    )

    st.markdown("---")
    st.caption("Sumber data: Beijing Multi-Site Air-Quality (PRSA), Mar 2013 - Feb 2017, 12 stasiun.")

if not selected_stations:
    selected_stations = all_stations

mask = (
    data["station"].isin(selected_stations)
    & (data["datetime"].dt.date >= start_date)
    & (data["datetime"].dt.date <= end_date)
)
fdata = data.loc[mask]


# HEADER

st.markdown(
    f"""
    <div class="app-header">
        {icon("station", 34)}
        <h1>Beijing Air Quality Report</h1>
        <p class="app-subtitle">Dashboard eksploratif konsentrasi polutan udara pada 12 stasiun pemantauan, 2013-2017</p>
        <p class="app-author">Weka Surajati Sudanta &middot; weka29januari@gmail.com</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if fdata.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih. Ubah filter pada panel samping.")
    st.stop()


# KPI

avg_val = fdata[pollutant].mean()
top_station = fdata.groupby("station")["PM2.5"].mean().idxmax()
top_value = fdata.groupby("station")["PM2.5"].mean().max()
pct_unhealthy = fdata["kategori_pm25"].isin(
    ["Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"]
).mean() * 100
n_days = (fdata["datetime"].max() - fdata["datetime"].min()).days + 1

k1, k2, k3, k4 = st.columns(4)
kpi_defs = [
    (k1, "gauge", f"Rata-rata {pollutant}", f"{avg_val:.1f}", "µg/m³ (CO dalam mg/m³) pada cakupan filter"),
    (k2, "smoke", "Stasiun Terpolusi", top_station, f"rata-rata PM2.5 {top_value:.1f} µg/m³"),
    (k3, "trend", "Waktu Kategori Tidak Sehat+", f"{pct_unhealthy:.1f}%", "dari seluruh jam observasi terfilter"),
    (k4, "calendar", "Cakupan Waktu", f"{n_days:,} hari".replace(",", "."), f"{len(selected_stations)} stasiun terpilih"),
]
for col, ic, label, value, sub in kpi_defs:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-label">{label}</span>
                    {icon(ic, 18)}
                </div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# SECTION 1 - PERBANDINGAN ANTAR STASIUN (Pertanyaan Bisnis 1)

st.markdown(
    f'<div class="section-title">{icon("smoke", 18)} Perbandingan Rata-rata PM2.5 Antar Stasiun</div>',
    unsafe_allow_html=True,
)

station_avg = (
    fdata.groupby("station")["PM2.5"].mean().sort_values(ascending=False).reset_index()
)
station_avg["color"] = station_avg["PM2.5"].apply(marker_color)

fig_station = go.Figure(
    go.Bar(
        x=station_avg["PM2.5"],
        y=station_avg["station"],
        orientation="h",
        marker_color=station_avg["color"],
        text=station_avg["PM2.5"].round(1),
        textposition="outside",
    )
)
fig_station.update_layout(
    height=430,
    plot_bgcolor="#141a22",
    paper_bgcolor="#141a22",
    font_color="#e7edf3",
    margin=dict(l=10, r=30, t=10, b=10),
    xaxis_title="Rata-rata PM2.5 (µg/m³)",
    yaxis=dict(autorange="reversed"),
    xaxis=dict(gridcolor="#28323e"),
)
st.plotly_chart(fig_station, use_container_width=True)
st.markdown(
    '<div class="note-box">Stasiun dengan batang berwarna merah berada pada rata-rata PM2.5 tertinggi '
    "(>= 85 µg/m³) dan menjadi kandidat prioritas kebijakan pengendalian polusi.</div>",
    unsafe_allow_html=True,
)


# SECTION 2 - POLA MUSIMAN (Pertanyaan Bisnis 2)

st.markdown(
    f'<div class="section-title">{icon("trend", 18)} Pola Musiman Konsentrasi PM2.5 dan PM10</div>',
    unsafe_allow_html=True,
)

monthly = fdata.groupby("month")[["PM2.5", "PM10"]].mean().reindex(range(1, 13))
fig_month = go.Figure()
fig_month.add_trace(go.Scatter(
    x=[MONTH_LABEL[m] for m in monthly.index], y=monthly["PM2.5"],
    mode="lines+markers", name="PM2.5", line=dict(color="#d9534f", width=2.4),
))
fig_month.add_trace(go.Scatter(
    x=[MONTH_LABEL[m] for m in monthly.index], y=monthly["PM10"],
    mode="lines+markers", name="PM10", line=dict(color="#3d8bfd", width=2.4),
))
fig_month.update_layout(
    height=400,
    plot_bgcolor="#141a22",
    paper_bgcolor="#141a22",
    font_color="#e7edf3",
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_title="Rata-rata Konsentrasi (µg/m³)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(gridcolor="#28323e"),
    yaxis=dict(gridcolor="#28323e"),
)
st.plotly_chart(fig_month, use_container_width=True)
st.markdown(
    '<div class="note-box">Konsentrasi memuncak pada periode Desember-Januari dan berada pada titik '
    "terendah di sekitar Agustus, sejalan dengan musim pemanas ruangan di Beijing.</div>",
    unsafe_allow_html=True,
)


# SECTION 3 - ANALISIS LANJUTAN: BINNING + GEOSPATIAL

st.markdown(
    f'<div class="section-title">{icon("layers", 18)} Analisis Lanjutan: Kategori Kualitas Udara &amp; Sebaran Geografis</div>',
    unsafe_allow_html=True,
)

col_bin, col_map = st.columns([1.05, 1])

with col_bin:
    st.caption("Distribusi kategori kualitas udara (binning PM2.5) per stasiun")
    cross = pd.crosstab(fdata["station"], fdata["kategori_pm25"], normalize="index") * 100
    cross = cross.reindex(columns=CATEGORY_ORDER, fill_value=0)
    cross = cross.loc[cross.sum(axis=1).sort_values().index]

    fig_bin = go.Figure()
    for cat in CATEGORY_ORDER:
        fig_bin.add_trace(go.Bar(
            y=cross.index, x=cross[cat], name=cat, orientation="h",
            marker_color=CATEGORY_COLOR[cat],
        ))
    fig_bin.update_layout(
        barmode="stack",
        height=430,
        plot_bgcolor="#141a22",
        paper_bgcolor="#141a22",
        font_color="#e7edf3",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Proporsi Waktu (%)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, font=dict(size=9)),
        xaxis=dict(gridcolor="#28323e"),
    )
    st.plotly_chart(fig_bin, use_container_width=True)

with col_map:
    st.caption("Peta rata-rata PM2.5 per stasiun (radius & warna mengikuti tingkat polusi)")
    map_avg = fdata.groupby("station")["PM2.5"].mean()

    m = folium.Map(location=[40.05, 116.4], zoom_start=8, tiles="OpenStreetMap")
    for station in selected_stations:
        if station not in STATION_COORDS or station not in map_avg.index:
            continue
        lat, lon = STATION_COORDS[station]
        val = map_avg[station]
        folium.CircleMarker(
            location=[lat, lon],
            radius=9 + (val / 10),
            color=marker_color(val),
            fill=True,
            fill_color=marker_color(val),
            fill_opacity=0.75,
            weight=1.5,
            popup=f"{station}: {val:.1f} µg/m³",
            tooltip=station,
        ).add_to(m)
    st_folium(m, height=430, use_container_width=True, returned_objects=[])


# TABEL RINGKASAN & UNDUH DATA

st.markdown(
    f'<div class="section-title">{icon("calendar", 18)} Ringkasan per Stasiun</div>',
    unsafe_allow_html=True,
)
summary = (
    fdata.groupby("station")
    .agg(
        rata_pm25=("PM2.5", "mean"),
        rata_pm10=("PM10", "mean"),
        maksimum_pm25=("PM2.5", "max"),
        jumlah_observasi=("PM2.5", "count"),
    )
    .round(1)
    .sort_values("rata_pm25", ascending=False)
    .reset_index()
)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.download_button(
    "Unduh data terfilter (CSV)",
    data=fdata.to_csv(index=False).encode("utf-8"),
    file_name="air_quality_filtered.csv",
    mime="text/csv",
)

# INSIGHT PENUTUP

clean_station = station_avg.iloc[-1]["station"]
clean_value = station_avg.iloc[-1]["PM2.5"]
peak_month = MONTH_LABEL[monthly["PM2.5"].idxmax()]

st.markdown(
    f"""
    <div class="note-box" style="margin-top:26px;">
        <strong style="color:var(--text-0);">Insight:</strong>
        Pada cakupan data yang dipilih, kualitas udara paling buruk tercatat di <strong>{top_station}</strong>
        (rata-rata PM2.5 {top_value:.1f} µg/m³) dan paling baik di <strong>{clean_station}</strong>
        ({clean_value:.1f} µg/m³), dengan puncak polusi terjadi pada bulan <strong>{peak_month}</strong>.
        Sekitar <strong>{pct_unhealthy:.1f}%</strong> waktu observasi berada pada kategori tidak sehat ke atas,
        menandakan perlunya perhatian lebih pada musim dingin dan wilayah urban padat.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<footer class="app-footer">Air Quality Dataset - Beijing Multi-Site Air-Quality (PRSA), 12 stasiun, Maret 2013 - Februari 2017</footer>',
    unsafe_allow_html=True,
)
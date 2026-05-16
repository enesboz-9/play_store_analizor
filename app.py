"""
AppVentures v2: Mobil Girişimler İçin Profesyonel Pazar Analizi & Fırsat Radarı
B2B SaaS Dashboard — Dark Mode, Plotly, Streamlit
"""

import re
import warnings
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ─────────────────────────── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="AppVentures | Pazar Analizi",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── GLOBAL STYLE ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stApp"] {
    background-color: #04091a;
    color: #e2e8f0;
    font-family: 'Space Grotesk', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070e24 0%, #0a1432 100%);
    border-right: 1px solid rgba(56,189,248,0.15);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 { color: #38bdf8; }
[data-testid="stTabs"] button {
    background: transparent !important;
    color: #64748b !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 600; font-size: 0.9rem;
    padding: 0.6rem 1rem !important;
    transition: all .2s;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
    background: rgba(56,189,248,0.05) !important;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,rgba(15,34,64,0.9),rgba(7,18,40,0.95));
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 14px;
    padding: 1.1rem 1.3rem !important;
    backdrop-filter: blur(10px);
    transition: border-color .2s;
}
[data-testid="stMetric"]:hover { border-color: rgba(56,189,248,0.45); }
[data-testid="stMetricLabel"]  { color: #64748b !important; font-size: .78rem; letter-spacing:.05em; text-transform:uppercase; }
[data-testid="stMetricValue"]  { color: #38bdf8 !important; font-weight: 700; font-size:1.6rem !important; }
[data-testid="stMetricDelta"]  { font-size: .78rem; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid rgba(56,189,248,0.15); }
h1 { color: #38bdf8 !important; }
h2, h3 { color: #7dd3fc !important; }
hr { border-color: rgba(56,189,248,0.12) !important; }
[data-testid="stAlert"] { border-radius: 10px; }
.stSelectbox div[data-baseweb], .stMultiSelect div[data-baseweb] {
    background-color: rgba(15,34,64,0.8) !important;
    border-color: rgba(56,189,248,0.2) !important;
    border-radius: 8px !important;
}
.stSlider > div { color: #38bdf8; }
.neon-badge {
    display: inline-block;
    background: rgba(56,189,248,.12);
    border: 1px solid rgba(56,189,248,0.4);
    color: #38bdf8; border-radius: 20px;
    padding: 2px 12px; font-size: .75rem;
    font-weight: 700; letter-spacing: .06em;
}
.green-badge {
    display: inline-block;
    background: rgba(52,211,153,.12);
    border: 1px solid rgba(52,211,153,0.4);
    color: #34d399; border-radius: 20px;
    padding: 2px 12px; font-size: .75rem;
    font-weight: 700; letter-spacing: .06em;
}
.amber-badge {
    display: inline-block;
    background: rgba(245,158,11,.12);
    border: 1px solid rgba(245,158,11,0.4);
    color: #f59e0b; border-radius: 20px;
    padding: 2px 12px; font-size: .75rem;
    font-weight: 700; letter-spacing: .06em;
}
.opp-card {
    background: linear-gradient(135deg,rgba(15,34,64,0.7),rgba(7,18,40,0.9));
    border: 1px solid rgba(30,58,95,0.8);
    border-left: 4px solid #f59e0b;
    border-radius: 12px; padding: 1.1rem 1.3rem;
    margin-bottom: .8rem;
    backdrop-filter: blur(6px);
    transition: border-left-color .2s, transform .2s;
}
.opp-card:hover { transform: translateX(4px); border-left-color: #38bdf8; }
.opp-card h4 { color: #fbbf24; margin:0 0 .4rem 0; font-size:1.05rem; }
.opp-card p  { color: #94a3b8; margin:0; font-size:.85rem; line-height:1.6; }
.insight-card {
    background: linear-gradient(135deg,rgba(15,34,64,0.6),rgba(7,18,40,0.8));
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 12px; padding: 1.2rem;
    margin-bottom: 1rem;
}
.insight-card .insight-title { color: #7dd3fc; font-weight:700; font-size:.95rem; margin-bottom:.5rem; }
.insight-card p { color: #94a3b8; font-size:.85rem; line-height:1.6; margin:0; }
.word-row {
    display:flex; align-items:center; gap:1rem;
    padding:.45rem .7rem; border-radius:8px;
    margin-bottom:.35rem;
    background:rgba(15,34,64,0.5);
    border: 1px solid rgba(56,189,248,0.06);
}
.word-bar { height:7px; border-radius:4px; background:linear-gradient(90deg,#7f1d1d,#ef4444); }
.kpi-header {
    padding: 1.8rem 0 .8rem 0;
}
.kpi-header h1 {
    margin:0; font-size:2.2rem; letter-spacing:-.03em;
    background: linear-gradient(90deg,#38bdf8,#818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi-header p { color:#475569; margin:.3rem 0 0 0; font-size:1rem; }
.roi-card {
    background: linear-gradient(135deg,rgba(52,211,153,0.08),rgba(7,18,40,0.95));
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 14px; padding: 1.4rem;
    text-align: center;
}
.roi-card .roi-value { color: #34d399; font-size: 2rem; font-weight: 700; }
.roi-card .roi-label { color: #64748b; font-size: .8rem; text-transform: uppercase; letter-spacing:.05em; margin-top:.2rem; }
.filter-section {
    background: rgba(56,189,248,0.04);
    border: 1px solid rgba(56,189,248,0.1);
    border-radius: 10px;
    padding: .8rem 1rem;
    margin-bottom: .8rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── DATA LOADING ──────────────────────────────────
import urllib.request
import requests
from pathlib import Path
_BASE = Path(__file__).parent

_CACHE_DIR = Path("/tmp") if Path("/tmp").exists() else _BASE
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_REMOTE_URLS = {
    "Google-Playstore.csv": (
        "https://huggingface.co/datasets/enesboz9/google-playstore/resolve/main/Google-Playstore.csv?download=true"
    ),
    "googleplaystore_user_reviews.csv": (
        "https://raw.githubusercontent.com/enesboz-9/play_store_analizor/main/googleplaystore_user_reviews.csv"
    ),
}

def _lfs_pointer(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            header = f.read(50)
        return header.startswith(b"version https://git-lfs")
    except Exception:
        return False

def _find_or_download(*filenames):
    search_dirs = [_BASE, _BASE / "data", _CACHE_DIR]
    for filename in filenames:
        for d in search_dirs:
            candidate = d / filename
            if candidate.exists() and not _lfs_pointer(candidate):
                return str(candidate)
    for filename in filenames:
        if filename in _REMOTE_URLS:
            dest = _CACHE_DIR / filename
            url  = _REMOTE_URLS[filename]
            if not dest.exists() or _lfs_pointer(dest):
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    with requests.get(url, headers=headers, stream=True, timeout=300) as r:
                        r.raise_for_status()
                        with open(dest, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    st.rerun()
                except Exception as e:
                    st.error(f"**{filename} indirilemedi.**\n\nHata: `{e}`\n\nURL: `{url}`")
                    raise
            else:
                return str(dest)
    raise FileNotFoundError(f"Şu dosyalardan biri bulunamadı ve indirilemedi: {filenames}")

APPS_PATH    = _find_or_download("Google-Playstore.csv", "googleplaystore.csv")
REVIEWS_PATH = _find_or_download("googleplaystore_user_reviews.csv")
_IS_NEW_FORMAT = Path(APPS_PATH).name == "Google-Playstore.csv"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(7,18,40,0.7)",
    font=dict(color="#e2e8f0", family="Space Grotesk"),
    title_font=dict(color="#7dd3fc", size=15),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(56,189,248,0.2)", borderwidth=1),
    xaxis=dict(gridcolor="rgba(30,58,95,0.6)", zerolinecolor="rgba(30,58,95,0.6)"),
    yaxis=dict(gridcolor="rgba(30,58,95,0.6)", zerolinecolor="rgba(30,58,95,0.6)"),
    colorway=["#38bdf8","#818cf8","#34d399","#f59e0b","#f472b6",
               "#60a5fa","#a78bfa","#4ade80","#fb923c","#e879f9"],
    margin=dict(l=10, r=10, t=50, b=10),
)

def _fmt_layout(fig: go.Figure, **extra) -> go.Figure:
    layout = {**PLOTLY_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig


@st.cache_data(show_spinner="Veriler yükleniyor…")
def load_apps() -> pd.DataFrame:
    if _IS_NEW_FORMAT:
        df = pd.read_csv(APPS_PATH, on_bad_lines="skip", low_memory=False)
        df = df.rename(columns={
            "App Name":       "App",
            "Rating Count":   "Reviews",
            "Minimum Installs": "Installs_num_raw",
        })
        df["Is_Free"] = df["Free"].astype(str).str.strip().str.lower() == "true"
        df["Price_num"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
        min_inst = pd.to_numeric(df.get("Installs_num_raw", pd.Series(dtype="float")), errors="coerce")
        str_inst = df["Installs"].astype(str).str.replace(",","",regex=False).str.replace("+","",regex=False).str.strip()
        df["Installs_num"] = min_inst.combine_first(pd.to_numeric(str_inst, errors="coerce"))
    else:
        df = pd.read_csv(APPS_PATH, on_bad_lines="skip")
        def clean_installs(v):
            if pd.isna(v): return np.nan
            v = str(v).replace(",","").replace("+","").strip()
            try: return int(v)
            except ValueError: return np.nan
        df["Installs_num"] = df["Installs"].apply(clean_installs)
        df["Reviews"]      = pd.to_numeric(df["Reviews"], errors="coerce")
        df["Price_num"]    = df["Price"].str.replace(r"[\$,]","",regex=True).apply(pd.to_numeric, errors="coerce").fillna(0)
        df["Is_Free"]      = df["Type"].str.strip() == "Free"

    def clean_size(v):
        if pd.isna(v): return np.nan
        v = str(v).strip()
        if "Varies" in v or v in ("","nan"): return np.nan
        if v.endswith("M"):
            try: return float(v[:-1])
            except: return np.nan
        if v.endswith("k"):
            try: return float(v[:-1]) / 1024
            except: return np.nan
        try: return float(v) / (1024*1024)
        except: return np.nan

    df["Size_MB"] = df["Size"].apply(clean_size)
    df["Rating"]  = pd.to_numeric(df["Rating"], errors="coerce").astype("float32")
    df = df[df["Rating"].between(1,5,inclusive="both") | df["Rating"].isna()]
    df = df[df["Category"].notna()]
    df = df[~df["Category"].isin(["1.9"])]
    df["Category_Clean"] = df["Category"].str.replace("_"," ",regex=False).str.title()

    keep_cols = ["App","Category","Category_Clean","Rating","Reviews",
                 "Installs_num","Size_MB","Is_Free","Price_num","Content Rating"]
    for opt in ["Last Updated","Released","Editors Choice","Ad Supported","In App Purchases"]:
        if opt in df.columns: keep_cols.append(opt)
    df = df[[c for c in keep_cols if c in df.columns]].copy()
    return df


@st.cache_data(show_spinner="Yorumlar yükleniyor…")
def load_reviews() -> pd.DataFrame:
    df = pd.read_csv(REVIEWS_PATH, on_bad_lines="skip")
    df["Translated_Review"] = df["Translated_Review"].fillna("")
    df["Sentiment"] = df["Sentiment"].fillna("Unknown")
    return df


apps_df    = load_apps()
reviews_df = load_reviews()

TOTAL_APPS = len(apps_df)
ALL_CATS   = sorted(apps_df["Category_Clean"].dropna().unique().tolist())
TOTAL_CATS = apps_df["Category_Clean"].nunique()

# Sidebar bilgi banner — tam sayı göster
if _IS_NEW_FORMAT:
    st.sidebar.success(
        f"✅ **Yeni veri seti aktif**\n\n"
        f"📱 **{TOTAL_APPS:,}** uygulama\n\n"
        f"🗂️ **{TOTAL_CATS}** kategori"
    )

# ─────────────────────────── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 AppVentures")
    st.markdown("<span class='neon-badge'>B2B Pazar Zekası v2</span>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Global Filtreler ──
    st.markdown("### 🔍 Global Filtreler")

    selected_cats = st.multiselect(
        "Kategoriler",
        options=ALL_CATS,
        default=ALL_CATS,
        help="Boş bırakılırsa tüm kategoriler seçilir",
    )

    rating_range = st.slider(
        "Puan Aralığı",
        min_value=1.0, max_value=5.0,
        value=(1.0, 5.0), step=0.1,
        help="Filtrelenecek minimum ve maksimum puan",
    )

    min_installs = st.select_slider(
        "Min. İndirme",
        options=[0, 100, 1_000, 10_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000],
        value=0,
        format_func=lambda x: f"{x:,}+" if x else "Tümü",
    )

    col_free, col_paid = st.columns(2)
    show_free = col_free.checkbox("Ücretsiz", value=True)
    show_paid = col_paid.checkbox("Ücretli",  value=True)

    st.markdown("---")
    # ── Gelişmiş Filtreler ──
    with st.expander("⚙️ Gelişmiş Filtreler", expanded=False):
        min_reviews = st.number_input(
            "Min. Değerlendirme Sayısı",
            min_value=0, value=0, step=100,
            help="Bu sayının altındaki uygulamaları filtrele",
        )
        content_ratings = []
        if "Content Rating" in apps_df.columns:
            cr_opts = sorted(apps_df["Content Rating"].dropna().unique().tolist())
            content_ratings = st.multiselect(
                "İçerik Derecelendirmesi",
                options=cr_opts,
                default=cr_opts,
            )
        min_size = st.slider("Min. Boyut (MB)", 0.0, 500.0, 0.0, 5.0)
        max_size = st.slider("Max. Boyut (MB)", 0.0, 500.0, 500.0, 5.0)

    st.markdown("---")
    # ── Fırsat Eşikleri ──
    st.markdown("### ⚡ Fırsat Eşikleri")
    opp_min_installs = st.slider(
        "Min İndirme (M)",
        min_value=0.1, max_value=50.0, value=10.0, step=0.5,
    )
    opp_max_rating = st.slider(
        "Max Puan",
        min_value=3.0, max_value=4.9, value=4.2, step=0.05,
    )
    opp_min_apps = st.slider(
        "Min Uygulama Sayısı (kategoride)",
        min_value=1, max_value=100, value=5,
    )

    st.markdown("---")
    st.caption(f"Veri: Kaggle Google Play Store · {'~2.3M' if _IS_NEW_FORMAT else '~10K'} uygulama")


# ─────────────────────────── FILTER ────────────────────────────────────────
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    cats = selected_cats if selected_cats else ALL_CATS
    mask = df["Category_Clean"].isin(cats)
    # Rating range
    mask &= (df["Rating"].isna()) | (df["Rating"].between(rating_range[0], rating_range[1]))
    # Min installs
    if min_installs:
        mask &= df["Installs_num"] >= min_installs
    # Free/paid
    type_mask = pd.Series([False]*len(df), index=df.index)
    if show_free: type_mask |= df["Is_Free"]
    if show_paid: type_mask |= ~df["Is_Free"]
    mask &= type_mask
    # Min reviews
    if min_reviews > 0 and "Reviews" in df.columns:
        mask &= df["Reviews"].fillna(0) >= min_reviews
    # Content rating
    if content_ratings and "Content Rating" in df.columns:
        mask &= df["Content Rating"].isin(content_ratings)
    # Size
    if "Size_MB" in df.columns:
        size_mask = df["Size_MB"].isna() | df["Size_MB"].between(min_size, max_size)
        mask &= size_mask
    return df[mask]

filtered_df = apply_filters(apps_df)

# ─────────────────────────── HEADER ────────────────────────────────────────
st.markdown(f"""
<div class="kpi-header">
  <h1>🚀 AppVentures</h1>
  <p>Mobil Girişimler İçin Profesyonel Pazar Analizi &amp; Fırsat Radarı</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────── KPI STRIP ─────────────────────────────────────
kc = st.columns(6)
kc[0].metric("📱 Toplam Uygulama",  f"{TOTAL_APPS:,}", help="Veri setindeki toplam uygulama sayısı")
kc[1].metric("🔍 Filtreli",          f"{len(filtered_df):,}", delta=f"{len(filtered_df)/TOTAL_APPS*100:.1f}% kapsam")
kc[2].metric("⭐ Ort. Puan",         f"{filtered_df['Rating'].mean():.2f}" if not filtered_df.empty else "—")
median_inst = filtered_df["Installs_num"].median() if not filtered_df.empty else 0
kc[3].metric("📥 Medyan İndirme",    f"{int(median_inst):,}" if pd.notna(median_inst) else "—")
kc[4].metric("🆓 Ücretsiz Oran",     f"{filtered_df['Is_Free'].mean()*100:.0f}%" if not filtered_df.empty else "—")
kc[5].metric("🗂️ Kategori",          f"{filtered_df['Category_Clean'].nunique()}")

st.markdown("---")

# ─────────────────────────── TABS ──────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔬 Pazar Röntgeni",
    "🎯 Fırsat Radarı",
    "🏆 Rekabet Analizi",
    "💰 Gelir & Fiyat Stratejisi",
    "💬 Kullanıcı Sesi",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PAZAR RÖNTGENİ
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if filtered_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı.")
        st.stop()

    cat_agg = (
        filtered_df
        .groupby("Category_Clean", as_index=False)
        .agg(
            app_count      =("App",          "count"),
            avg_rating     =("Rating",        "mean"),
            median_rating  =("Rating",        "median"),
            total_installs =("Installs_num",  "sum"),
            median_installs=("Installs_num",  "median"),
            free_pct       =("Is_Free",       "mean"),
            total_reviews  =("Reviews",       "sum"),
        )
        .sort_values("total_installs", ascending=False)
    )
    cat_agg["avg_rating"]       = cat_agg["avg_rating"].round(2)
    cat_agg["total_installs_M"] = (cat_agg["total_installs"] / 1e6).round(1)
    cat_agg["median_installs_k"]= (cat_agg["median_installs"] / 1e3).round(1)
    cat_agg["free_pct_label"]   = (cat_agg["free_pct"]*100).round(0).astype(int).astype(str) + "%"
    cat_agg["competition_score"]= (cat_agg["app_count"] / cat_agg["app_count"].max() * 100).round(0)

    st.markdown("### 🏭 Pazar Haritası")
    st.caption("Kategorilere göre rekabet yoğunluğu, talep ve memnuniyet dağılımı")

    col_a, col_b = st.columns([3,2], gap="medium")
    with col_a:
        fig_bubble = px.scatter(
            cat_agg,
            x="avg_rating", y="app_count",
            size="total_installs_M",
            color="Category_Clean",
            hover_name="Category_Clean",
            hover_data={
                "avg_rating":":.2f",
                "app_count":True,
                "total_installs_M":":.1f",
                "free_pct_label":True,
                "Category_Clean":False,
            },
            labels={
                "avg_rating":"Ort. Puan",
                "app_count":"Uygulama Sayısı",
                "total_installs_M":"İndirme (M)",
                "free_pct_label":"Ücretsiz Oran",
            },
            title="Kategori Haritası: Rekabet × Puan × Talep",
            size_max=60,
        )
        _fmt_layout(fig_bubble, height=480)
        fig_bubble.update_traces(marker=dict(opacity=0.82, line=dict(width=1, color="#04091a")))
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_b:
        top15 = cat_agg.nlargest(15,"app_count").sort_values("app_count")
        fig_bar = go.Figure(go.Bar(
            y=top15["Category_Clean"], x=top15["app_count"],
            orientation="h",
            marker=dict(
                color=top15["avg_rating"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
                showscale=True,
                colorbar=dict(title="Puan", tickfont=dict(color="#94a3b8"), len=0.6),
                line=dict(width=0),
            ),
            text=top15["app_count"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(color="#e2e8f0", size=10),
            hovertemplate="<b>%{y}</b><br>%{x:,} uygulama<extra></extra>",
        ))
        _fmt_layout(fig_bar, title="En Kalabalık 15 Kategori", height=480)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 İndirme & Puan Dağılımları")

    col_c, col_d = st.columns(2, gap="medium")
    with col_c:
        top_inst = cat_agg.nlargest(12,"total_installs_M")
        fig_inst = px.bar(
            top_inst.sort_values("total_installs_M"),
            y="Category_Clean", x="total_installs_M",
            orientation="h",
            color="avg_rating",
            color_continuous_scale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
            labels={"total_installs_M":"Toplam İndirme (M)","Category_Clean":"Kategori","avg_rating":"Puan"},
            title="Toplam İndirme — Top 12 Kategori",
        )
        _fmt_layout(fig_inst, height=420)
        st.plotly_chart(fig_inst, use_container_width=True)

    with col_d:
        fig_rating_box = px.box(
            filtered_df[filtered_df["Rating"].notna()].sample(min(50000,len(filtered_df))),
            x="Category_Clean", y="Rating",
            color="Is_Free",
            color_discrete_map={True:"#38bdf8", False:"#f59e0b"},
            labels={"Category_Clean":"Kategori","Rating":"Puan","Is_Free":"Ücretsiz"},
            title="Puan Dağılımı (Box Plot)",
        )
        fig_rating_box.update_layout(xaxis_tickangle=-45, showlegend=True)
        _fmt_layout(fig_rating_box, height=420)
        st.plotly_chart(fig_rating_box, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔥 Pazar Isı Haritası")
    st.caption("Kategorilerdeki uygulama yoğunluğu ve puan dağılımı")

    rating_bins = ["1-2","2-3","3-4","4-4.5","4.5-5"]
    def rate_bin(r):
        if pd.isna(r): return None
        if r < 2: return "1-2"
        if r < 3: return "2-3"
        if r < 4: return "3-4"
        if r < 4.5: return "4-4.5"
        return "4.5-5"

    heat_df = filtered_df.copy()
    heat_df["Rating_Bin"] = heat_df["Rating"].apply(rate_bin)
    heat_df = heat_df.dropna(subset=["Rating_Bin"])

    top_cats_heat = cat_agg.nlargest(20,"app_count")["Category_Clean"].tolist()
    heat_pivot = (
        heat_df[heat_df["Category_Clean"].isin(top_cats_heat)]
        .groupby(["Category_Clean","Rating_Bin"])
        .size().reset_index(name="count")
        .pivot(index="Category_Clean", columns="Rating_Bin", values="count")
        .reindex(columns=rating_bins).fillna(0)
    )

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0,"#04091a"],[0.3,"#0f2240"],[0.7,"#38bdf8"],[1,"#f472b6"]],
        hovertemplate="<b>%{y}</b><br>Puan: %{x}<br>Uygulama: %{z:,}<extra></extra>",
        text=heat_pivot.values.astype(int),
        texttemplate="%{text:,}",
        textfont=dict(size=9, color="#e2e8f0"),
    ))
    _fmt_layout(fig_heat, title="Kategori × Puan Aralığı Dağılımı", height=520,
                xaxis=dict(title="Puan Aralığı"), yaxis=dict(title=""))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 Pazar Büyüklüğü Özet Tablosu")
    show_cols = {
        "Category_Clean":"Kategori",
        "app_count":"Uygulama Sayısı",
        "avg_rating":"Ort. Puan",
        "total_installs_M":"Toplam İndirme (M)",
        "median_installs_k":"Medyan İndirme (K)",
        "free_pct_label":"Ücretsiz Oran",
        "competition_score":"Rekabet Skoru",
    }
    display_cat = cat_agg[[c for c in show_cols]].rename(columns=show_cols).sort_values("Toplam İndirme (M)", ascending=False)
    st.dataframe(display_cat, use_container_width=True, height=420, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FIRSAT RADARI
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if filtered_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı.")
        st.stop()

    opp_threshold_inst = opp_min_installs * 1_000_000

    cat_opp = (
        filtered_df
        .groupby("Category_Clean", as_index=False)
        .agg(
            app_count      =("App",          "count"),
            avg_rating     =("Rating",        "mean"),
            median_rating  =("Rating",        "median"),
            total_installs =("Installs_num",  "sum"),
            high_inst_apps =("Installs_num",  lambda x: (x >= opp_threshold_inst).sum()),
            total_reviews  =("Reviews",       "sum"),
        )
    )
    cat_opp["avg_rating"]   = cat_opp["avg_rating"].round(2)
    cat_opp["total_M"]      = (cat_opp["total_installs"] / 1e6).round(1)
    cat_opp["opp_score"]    = (cat_opp["total_M"] / cat_opp["avg_rating"].clip(lower=0.1)).round(1)
    cat_opp["market_gap"]   = ((5 - cat_opp["avg_rating"]) * cat_opp["total_M"]).round(1)

    cat_opp_filtered = cat_opp[
        (cat_opp["total_M"] >= opp_min_installs) &
        (cat_opp["avg_rating"] <= opp_max_rating) &
        (cat_opp["app_count"] >= opp_min_apps)
    ].sort_values("opp_score", ascending=False)

    opp_apps = filtered_df[
        (filtered_df["Installs_num"] >= opp_threshold_inst) &
        (filtered_df["Rating"] <= opp_max_rating) &
        filtered_df["Rating"].notna()
    ].copy()

    st.markdown("### 🎯 Fırsat Algoritması")
    st.markdown(
        f"> **Yüksek talep** (>{opp_min_installs:.1f}M indirme) "
        f"**ama düşük memnuniyet** (<{opp_max_rating} puan) olan alanlar. "
        f"Girişimci için altın bölge — müşteri var, çözüm yok."
    )

    # KPI strip
    ok1, ok2, ok3, ok4 = st.columns(4)
    ok1.metric("🎯 Fırsat Kategorisi", f"{len(cat_opp_filtered)}")
    ok2.metric("📱 Fırsat Uygulaması", f"{len(opp_apps):,}")
    best_opp = cat_opp_filtered.iloc[0]["Category_Clean"] if not cat_opp_filtered.empty else "—"
    ok3.metric("🏆 En İyi Fırsat",     best_opp)
    avg_gap = cat_opp_filtered["market_gap"].mean() if not cat_opp_filtered.empty else 0
    ok4.metric("💡 Ort. Pazar Açığı",  f"{avg_gap:.0f}")

    st.markdown("---")

    # ── Quadrant chart ──
    col_q1, col_q2 = st.columns([3,2], gap="medium")
    with col_q1:
        fig_quad = go.Figure()
        x_mid = opp_max_rating
        ymax  = cat_opp["total_M"].max() * 1.15 if not cat_opp.empty else 100

        fig_quad.add_shape(type="rect", x0=1, y0=opp_min_installs, x1=x_mid, y1=ymax,
                            fillcolor="rgba(239,68,68,0.07)", line_width=0)
        fig_quad.add_shape(type="rect", x0=x_mid, y0=opp_min_installs, x1=5.1, y1=ymax,
                            fillcolor="rgba(52,211,153,0.04)", line_width=0)
        fig_quad.add_annotation(x=(1+x_mid)/2, y=ymax*0.92,
                                 text="🔥 FIRSAT BÖLGESİ", showarrow=False,
                                 font=dict(color="#f87171",size=11))
        fig_quad.add_annotation(x=(x_mid+5)/2, y=ymax*0.92,
                                 text="✅ DOYMUŞ PAZAR", showarrow=False,
                                 font=dict(color="#6ee7b7",size=11))

        fig_quad.add_trace(go.Scatter(
            x=cat_opp["avg_rating"], y=cat_opp["total_M"],
            mode="markers+text",
            text=cat_opp["Category_Clean"].str.split().str[0],
            textposition="top center",
            textfont=dict(size=8, color="#94a3b8"),
            marker=dict(
                size=(cat_opp["opp_score"].clip(upper=500)/8 + 7).clip(upper=45),
                color=cat_opp["avg_rating"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
                showscale=True,
                colorbar=dict(title="Puan", tickfont=dict(color="#94a3b8"), len=0.5),
                opacity=0.88,
                line=dict(color="#04091a", width=1),
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Ort. Puan: %{x:.2f}<br>"
                "Toplam İndirme: %{y:.1f}M<br>"
                "Fırsat Skoru: %{customdata[1]:.0f}<br>"
                "Pazar Açığı: %{customdata[2]:.0f}<extra></extra>"
            ),
            customdata=np.stack([cat_opp["Category_Clean"], cat_opp["opp_score"], cat_opp["market_gap"]], axis=1),
            name="Kategori",
        ))
        fig_quad.add_vline(x=opp_max_rating, line_dash="dash", line_color="#f59e0b",
                            annotation_text=f"Puan eşiği: {opp_max_rating}",
                            annotation_font_color="#f59e0b")
        fig_quad.add_hline(y=opp_min_installs, line_dash="dash", line_color="#38bdf8",
                            annotation_text=f"{opp_min_installs}M İndirme",
                            annotation_font_color="#38bdf8")
        _fmt_layout(fig_quad,
                    title="Talep × Memnuniyet Matrisi",
                    xaxis=dict(title="Ortalama Kullanıcı Puanı", range=[1,5.1], gridcolor="rgba(30,58,95,0.6)"),
                    yaxis=dict(title="Toplam İndirme (Milyon)", type="log", gridcolor="rgba(30,58,95,0.6)"),
                    height=500)
        st.plotly_chart(fig_quad, use_container_width=True)

    with col_q2:
        st.markdown("#### 🏅 Fırsat Skoru Sıralaması")
        if not cat_opp_filtered.empty:
            fig_opp_rank = go.Figure(go.Bar(
                y=cat_opp_filtered.head(10)["Category_Clean"].str[:20][::-1],
                x=cat_opp_filtered.head(10)["opp_score"][::-1],
                orientation="h",
                marker=dict(
                    color=cat_opp_filtered.head(10)["opp_score"][::-1],
                    colorscale=[[0,"#0f2240"],[1,"#f59e0b"]],
                    line=dict(width=0),
                ),
                text=cat_opp_filtered.head(10)["opp_score"][::-1].round(0).astype(int),
                textposition="outside",
                textfont=dict(color="#e2e8f0",size=10),
                hovertemplate="<b>%{y}</b><br>Skor: %{x:.0f}<extra></extra>",
            ))
            _fmt_layout(fig_opp_rank, title="Top 10 Fırsat Kategorisi", height=360)
            st.plotly_chart(fig_opp_rank, use_container_width=True)
        else:
            st.info("Eşikleri gevşetin.")

        # Pazar açığı chart
        if not cat_opp_filtered.empty:
            fig_gap = px.bar(
                cat_opp_filtered.head(8),
                x="Category_Clean", y="market_gap",
                color="market_gap",
                color_continuous_scale=[[0,"#1e3a5f"],[1,"#ef4444"]],
                title="Pazar Açığı Skoru",
                labels={"Category_Clean":"","market_gap":"Açık Skoru"},
            )
            fig_gap.update_layout(xaxis_tickangle=-30, showlegend=False)
            _fmt_layout(fig_gap, height=260, margin=dict(l=10,r=10,t=40,b=60))
            st.plotly_chart(fig_gap, use_container_width=True)

    # ── Opportunity cards ──
    st.markdown("---")
    st.markdown("### 💡 Tespit Edilen Fırsatlar")

    if cat_opp_filtered.empty:
        st.info("Mevcut filtreler ile fırsat bulunamadı. Sol panelden eşikleri gevşetin.")
    else:
        for i, (_, row) in enumerate(cat_opp_filtered.iterrows()):
            demand  = "🔥 Çok Yüksek" if row["total_M"]>50 else ("⚡ Yüksek" if row["total_M"]>10 else "📈 Orta")
            sat     = "😤 Çok Düşük"  if row["avg_rating"]<3 else ("😐 Düşük" if row["avg_rating"]<3.5 else "😕 Orta-Altı")
            urgency = "🔴 ACİL" if row["opp_score"]>100 else ("🟡 YÜKSEK" if row["opp_score"]>50 else "🟢 ORTA")
            st.markdown(f"""
<div class="opp-card">
  <h4>🎯 {row['Category_Clean']} &nbsp;
    <span class="neon-badge">Fırsat Skoru: {row['opp_score']:.0f}</span> &nbsp;
    <span class="amber-badge">{urgency}</span>
  </h4>
  <p>
    📥 <b>{row['total_M']:.1f}M</b> toplam indirme &nbsp;|&nbsp;
    ⭐ Ort. puan <b>{row['avg_rating']:.2f}</b> &nbsp;|&nbsp;
    📱 <b>{row['app_count']:,}</b> uygulama &nbsp;|&nbsp;
    🎯 Pazar açığı: <b>{row['market_gap']:.0f}</b><br>
    Talep: {demand} &nbsp;•&nbsp; Memnuniyet: {sat}<br>
    👉 <em>Bu kategoride {row['app_count']:,} uygulama var ama kullanıcılar tatmin değil.
    Rakiplerin eksikliklerini kapatın, pazar payı kapın.</em>
  </p>
</div>
""", unsafe_allow_html=True)

    # ── Fırsat uygulamaları tablosu ──
    st.markdown("---")
    st.markdown(f"### 📋 Fırsat Uygulamaları ({len(opp_apps):,} adet)")
    st.caption(f">{opp_min_installs:.1f}M indirme VE <{opp_max_rating} puan olan uygulamalar")

    if not opp_apps.empty:
        display_cols = [c for c in ["App","Category_Clean","Rating","Installs_num","Is_Free","Reviews","Size_MB"] if c in opp_apps.columns]
        opp_show = opp_apps[display_cols].rename(columns={
            "Category_Clean":"Kategori","Rating":"Puan",
            "Installs_num":"İndirme","Is_Free":"Ücretsiz",
            "Reviews":"Değerlendirme","Size_MB":"Boyut (MB)",
        }).sort_values("İndirme", ascending=False).reset_index(drop=True)

        opp_show["İndirme"]      = opp_show["İndirme"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        opp_show["Değerlendirme"]= opp_show["Değerlendirme"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—") if "Değerlendirme" in opp_show.columns else "—"
        opp_show["Ücretsiz"]     = opp_show["Ücretsiz"].map({True:"✅","False":"💎"}) if "Ücretsiz" in opp_show.columns else "—"

        st.dataframe(opp_show, use_container_width=True, height=400, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — REKABET ANALİZİ
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if filtered_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı.")
        st.stop()

    st.markdown("### 🏆 Kategori Bazlı Rekabet Analizi")
    st.caption("Seçilen kategorilerde rekabeti derinlemesine inceleyin")

    sel_cat_comp = st.selectbox(
        "📂 Kategori Seçin",
        options=sorted(filtered_df["Category_Clean"].unique().tolist()),
        index=0,
    )

    cat_data = filtered_df[filtered_df["Category_Clean"] == sel_cat_comp].copy()

    # KPI
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("📱 Uygulama Sayısı",   f"{len(cat_data):,}")
    c2.metric("⭐ Ort. Puan",          f"{cat_data['Rating'].mean():.2f}" if not cat_data["Rating"].isna().all() else "—")
    c3.metric("📥 Toplam İndirme",     f"{cat_data['Installs_num'].sum()/1e6:.1f}M" if cat_data["Installs_num"].notna().any() else "—")
    c4.metric("🆓 Ücretsiz Oran",      f"{cat_data['Is_Free'].mean()*100:.0f}%")
    top_app_row = cat_data.nlargest(1,"Installs_num")
    top_app_name = top_app_row["App"].values[0][:20] if not top_app_row.empty else "—"
    c5.metric("🥇 Lider Uygulama",     top_app_name)

    st.markdown("---")
    col_r1, col_r2 = st.columns(2, gap="medium")

    with col_r1:
        # Top uygulamalar (indirme)
        top_apps_cat = cat_data.nlargest(15,"Installs_num").sort_values("Installs_num")
        fig_top = go.Figure(go.Bar(
            y=top_apps_cat["App"].str[:30],
            x=top_apps_cat["Installs_num"] / 1e6,
            orientation="h",
            marker=dict(
                color=top_apps_cat["Rating"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
                showscale=True,
                colorbar=dict(title="Puan", len=0.5, tickfont=dict(color="#94a3b8")),
                line=dict(width=0),
            ),
            text=top_apps_cat["Installs_num"].apply(lambda x: f"{x/1e6:.1f}M" if pd.notna(x) else "—"),
            textposition="outside", textfont=dict(color="#e2e8f0", size=9),
            hovertemplate="<b>%{y}</b><br>%{x:.2f}M indirme<extra></extra>",
        ))
        _fmt_layout(fig_top, title=f"Top 15 Uygulama — {sel_cat_comp}", height=480)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_r2:
        # Puan dağılımı histogram
        fig_rating_hist = px.histogram(
            cat_data[cat_data["Rating"].notna()], x="Rating",
            nbins=30, color="Is_Free",
            color_discrete_map={True:"#38bdf8",False:"#f59e0b"},
            labels={"Rating":"Puan","count":"Uygulama Sayısı","Is_Free":"Ücretsiz"},
            title=f"Puan Dağılımı — {sel_cat_comp}",
            opacity=0.8,
        )
        _fmt_layout(fig_rating_hist, height=250)
        st.plotly_chart(fig_rating_hist, use_container_width=True)

        # İndirme dağılımı
        inst_data = cat_data[cat_data["Installs_num"]>0].copy()
        if not inst_data.empty:
            fig_inst_hist = px.histogram(
                inst_data, x="Installs_num",
                nbins=30, color="Is_Free",
                color_discrete_map={True:"#38bdf8",False:"#f59e0b"},
                labels={"Installs_num":"İndirme Sayısı","count":"Uygulama Sayısı","Is_Free":"Ücretsiz"},
                title=f"İndirme Dağılımı — {sel_cat_comp}",
                log_x=True, opacity=0.8,
            )
            _fmt_layout(fig_inst_hist, height=250)
            st.plotly_chart(fig_inst_hist, use_container_width=True)

    st.markdown("---")

    # Scatter: Puan vs İndirme
    scatter_data = cat_data[cat_data["Rating"].notna() & cat_data["Installs_num"].notna()].copy()
    if not scatter_data.empty:
        fig_scatter = px.scatter(
            scatter_data.sample(min(2000, len(scatter_data))),
            x="Rating", y="Installs_num",
            color="Is_Free",
            size="Reviews" if "Reviews" in scatter_data.columns else None,
            color_discrete_map={True:"#38bdf8",False:"#f59e0b"},
            hover_name="App",
            labels={"Rating":"Puan","Installs_num":"İndirme","Is_Free":"Ücretsiz"},
            title=f"Puan × İndirme İlişkisi — {sel_cat_comp}",
            log_y=True,
            opacity=0.7,
            size_max=20,
        )
        _fmt_layout(fig_scatter, height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Tablo
    st.markdown(f"### 📋 {sel_cat_comp} — Tüm Uygulamalar")
    tbl_cols = [c for c in ["App","Rating","Installs_num","Reviews","Is_Free","Size_MB"] if c in cat_data.columns]
    tbl = cat_data[tbl_cols].rename(columns={
        "Installs_num":"İndirme","Is_Free":"Ücretsiz","Size_MB":"Boyut(MB)","Reviews":"Değerlendirme"
    }).sort_values("İndirme", ascending=False).reset_index(drop=True)
    if "İndirme" in tbl: tbl["İndirme"] = tbl["İndirme"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
    if "Ücretsiz" in tbl: tbl["Ücretsiz"] = tbl["Ücretsiz"].map({True:"✅",False:"💎"})
    st.dataframe(tbl, use_container_width=True, height=380, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — GELİR & FİYAT STRATEJİSİ
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if filtered_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı.")
        st.stop()

    st.markdown("### 💰 Gelir Modeli & Fiyatlandırma Analizi")

    free_df = filtered_df[filtered_df["Is_Free"]]
    paid_df = filtered_df[~filtered_df["Is_Free"]]

    p1,p2,p3,p4 = st.columns(4)
    p1.metric("🆓 Ücretsiz Uygulama",   f"{len(free_df):,}")
    p2.metric("💎 Ücretli Uygulama",    f"{len(paid_df):,}")
    avg_price = paid_df["Price_num"].mean() if not paid_df.empty else 0
    p3.metric("💲 Ort. Ücretli Fiyat",  f"${avg_price:.2f}")
    med_price = paid_df["Price_num"].median() if not paid_df.empty else 0
    p4.metric("💲 Med. Ücretli Fiyat",  f"${med_price:.2f}")

    st.markdown("---")
    col_p1, col_p2 = st.columns(2, gap="medium")

    with col_p1:
        # Ücretsiz vs Ücretli puan violin
        fig_violin = px.violin(
            filtered_df[filtered_df["Rating"].notna()].sample(min(20000,len(filtered_df))),
            x="Is_Free", y="Rating",
            color="Is_Free",
            color_discrete_map={True:"#38bdf8",False:"#f59e0b"},
            labels={"Is_Free":"Model","Rating":"Puan"},
            title="Puan Dağılımı: Ücretsiz vs Ücretli",
            box=True, points="suspectedoutliers",
        )
        fig_violin.update_layout(xaxis=dict(tickvals=[True,False],ticktext=["Ücretsiz","Ücretli"]),showlegend=False)
        _fmt_layout(fig_violin, height=380)
        st.plotly_chart(fig_violin, use_container_width=True)

    with col_p2:
        # Ücretsiz/Ücretli dağılımı kategori bazında
        price_cat = (
            filtered_df
            .groupby(["Category_Clean","Is_Free"], as_index=False)
            .agg(count=("App","count"), avg_installs=("Installs_num","mean"))
        )
        price_cat["Model"] = price_cat["Is_Free"].map({True:"Ücretsiz",False:"Ücretli"})
        top_cats_p = cat_agg.nlargest(12,"app_count")["Category_Clean"].tolist()
        fig_price_cat = px.bar(
            price_cat[price_cat["Category_Clean"].isin(top_cats_p)],
            x="Category_Clean", y="count", color="Model",
            barmode="stack",
            color_discrete_map={"Ücretsiz":"#38bdf8","Ücretli":"#f59e0b"},
            labels={"Category_Clean":"Kategori","count":"Uygulama Sayısı","Model":"Model"},
            title="Kategori × Model Dağılımı (Top 12)",
        )
        fig_price_cat.update_layout(xaxis_tickangle=-35)
        _fmt_layout(fig_price_cat, height=380)
        st.plotly_chart(fig_price_cat, use_container_width=True)

    st.markdown("---")
    # Fiyat aralığı analizi
    if not paid_df.empty and paid_df["Price_num"].notna().any():
        st.markdown("### 💲 Ücretli Uygulama Fiyat Analizi")

        price_valid = paid_df[paid_df["Price_num"].between(0.01, 200)].copy()
        if not price_valid.empty:
            def price_bucket(p):
                if p <= 0.99: return "$0.01–$0.99"
                if p <= 1.99: return "$1–$1.99"
                if p <= 2.99: return "$2–$2.99"
                if p <= 4.99: return "$3–$4.99"
                if p <= 9.99: return "$5–$9.99"
                if p <= 19.99: return "$10–$19.99"
                return "$20+"
            price_valid["Fiyat Aralığı"] = price_valid["Price_num"].apply(price_bucket)
            price_order = ["$0.01–$0.99","$1–$1.99","$2–$2.99","$3–$4.99","$5–$9.99","$10–$19.99","$20+"]

            col_pr1, col_pr2 = st.columns(2, gap="medium")
            with col_pr1:
                price_bucket_agg = price_valid.groupby("Fiyat Aralığı").agg(
                    count=("App","count"), avg_rating=("Rating","mean"),
                    avg_installs=("Installs_num","mean")
                ).reset_index().set_index("Fiyat Aralığı").reindex(price_order).dropna().reset_index()

                fig_price_dist = px.bar(
                    price_bucket_agg, x="Fiyat Aralığı", y="count",
                    color="avg_rating",
                    color_continuous_scale=[[0,"#ef4444"],[1,"#34d399"]],
                    labels={"count":"Uygulama Sayısı","avg_rating":"Ort. Puan"},
                    title="Fiyat Aralığı Dağılımı",
                )
                _fmt_layout(fig_price_dist, height=320)
                st.plotly_chart(fig_price_dist, use_container_width=True)

            with col_pr2:
                fig_price_rating = px.scatter(
                    price_valid.sample(min(3000,len(price_valid))),
                    x="Price_num", y="Rating",
                    size="Installs_num" if price_valid["Installs_num"].notna().any() else None,
                    color="Category_Clean",
                    hover_name="App",
                    labels={"Price_num":"Fiyat ($)","Rating":"Puan"},
                    title="Fiyat × Puan İlişkisi",
                    log_x=True, opacity=0.7, size_max=15,
                )
                _fmt_layout(fig_price_rating, height=320)
                st.plotly_chart(fig_price_rating, use_container_width=True)

    st.markdown("---")
    # Strateji önerileri
    st.markdown("### 🧭 Gelir Stratejisi Önerileri")
    free_avg   = free_df["Rating"].mean() if not free_df.empty else 0
    paid_avg   = paid_df["Rating"].mean() if not paid_df.empty else 0
    free_inst  = free_df["Installs_num"].median() if not free_df.empty else 0
    paid_inst  = paid_df["Installs_num"].median() if not paid_df.empty else 0

    si1,si2,si3 = st.columns(3, gap="medium")
    with si1:
        winner = "Ücretsiz" if (free_inst or 0) > (paid_inst or 0) else "Ücretli"
        ratio  = max(free_inst or 1, paid_inst or 1) / (min(free_inst or 1, paid_inst or 1) + 1)
        st.info(f"**📈 Büyüme Taktiği**\n\n{winner} model, medyan indirme açısından **{ratio:.1f}× daha fazla** erişim sağlıyor. Kullanıcı tabanını hızla büyütmek için freemium başlayın.")
    with si2:
        better = "Ücretli" if (paid_avg or 0)>(free_avg or 0) else "Ücretsiz"
        diff   = abs((paid_avg or 0)-(free_avg or 0))
        st.success(f"**⭐ Kalite Sinyali**\n\n{better} uygulamalar ortalamada **{diff:.2f} puan** daha yüksek. Premium segmentte kullanıcı tatminini ön plana çıkarın.")
    with si3:
        top_cat = cat_agg.nlargest(1,"total_installs_M")["Category_Clean"].values[0] if not cat_agg.empty else "—"
        st.warning(f"**🏆 Lider Kategori**\n\n**{top_cat}** kategorisi en fazla indirmeyi çekiyor. Bu alanda farklılaşan bir niş bulmak yüksek potansiyel taşıyor.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — KULLANICI SESİ
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 💬 Rakip Uygulama Zayıflık Analizi")
    st.caption("Negatif yorumları analiz ederek teknik zafiyetleri ve kullanıcı şikayetlerini keşfedin")

    reviewed_apps = sorted(reviews_df[reviews_df["Sentiment"]=="Negative"]["App"].unique().tolist())
    filtered_app_names = filtered_df["App"].unique().tolist()
    reviewed_and_filtered = [a for a in reviewed_apps if a in filtered_app_names]
    app_pool = reviewed_and_filtered if reviewed_and_filtered else reviewed_apps

    if not app_pool:
        st.warning("Seçilen filtrelerle eşleşen yorumlu uygulama bulunamadı.")
        st.stop()

    col_sel1, col_sel2 = st.columns([2,1])
    with col_sel1:
        selected_app = st.selectbox(
            "🔎 Analiz Edilecek Rakip Uygulama",
            options=app_pool, index=0,
            help="Sadece negatif yorumu olan uygulamalar listeleniyor",
        )
    with col_sel2:
        top_n_words = st.slider("Gösterilecek Kelime Sayısı", 10, 50, 25)

    neg_reviews = reviews_df[(reviews_df["App"]==selected_app)&(reviews_df["Sentiment"]=="Negative")]["Translated_Review"].dropna().tolist()
    pos_reviews = reviews_df[(reviews_df["App"]==selected_app)&(reviews_df["Sentiment"]=="Positive")]["Translated_Review"].dropna().tolist()
    neu_reviews = reviews_df[(reviews_df["App"]==selected_app)&(reviews_df["Sentiment"]=="Neutral")]["Translated_Review"].dropna().tolist()
    all_rev     = reviews_df[reviews_df["App"]==selected_app]
    total_reviews = len(all_rev)

    if not neg_reviews:
        st.info(f"**{selected_app}** için negatif yorum bulunamadı.")
        st.stop()

    app_info = apps_df[apps_df["App"]==selected_app].iloc[0] if selected_app in apps_df["App"].values else None

    # KPI
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("🔴 Negatif", len(neg_reviews))
    m2.metric("🟢 Pozitif", len(pos_reviews))
    m3.metric("😐 Nötr",    len(neu_reviews))
    m4.metric("📊 Toplam",  total_reviews)
    neg_rate = len(neg_reviews)/total_reviews*100 if total_reviews else 0
    m5.metric("⚠️ Şikayet Oranı", f"{neg_rate:.1f}%",
              delta="yüksek" if neg_rate>30 else "normal", delta_color="inverse")

    if app_info is not None:
        st.markdown(
            f"**Kategori:** {app_info.get('Category_Clean','—')} &nbsp;|&nbsp; "
            f"**Puan:** {app_info.get('Rating','—')} ⭐ &nbsp;|&nbsp; "
            f"**İndirme:** {app_info.get('Installs_num',0):,.0f} &nbsp;|&nbsp; "
            f"**Tip:** {'🆓 Ücretsiz' if app_info.get('Is_Free') else '💎 Ücretli'}"
        )

    st.markdown("---")

    STOPWORDS = {
        "the","a","an","and","or","but","is","was","are","were","be","been","being",
        "have","has","had","do","does","did","will","would","could","should","may",
        "might","shall","can","need","this","that","these","those","it","its","of",
        "in","on","at","to","for","with","from","by","about","as","into","through",
        "during","before","after","above","below","between","out","off","over","under",
        "then","once","i","me","my","we","our","you","your","he","she","they","them",
        "their","what","which","who","when","where","why","how","all","both","each",
        "so","if","because","while","app","application","game","just","like","really",
        "very","much","more","even","still","also","now","get","got","use","used",
        "using","good","great","bad","one","not","no","nan","s","t","don","doesn",
        "didn","isn","wasn","aren","hasn","haven","won","can","ve","re","ll","m",
        "am","im","ive","id","its","thats","youre","theyre",
    }

    def extract_words(reviews):
        text = " ".join(reviews).lower()
        words = re.findall(r"\b[a-z]{3,}\b", text)
        return [w for w in words if w not in STOPWORDS]

    neg_words = extract_words(neg_reviews)
    pos_words = extract_words(pos_reviews)
    word_freq = Counter(neg_words).most_common(top_n_words)
    pos_word_freq = Counter(pos_words).most_common(top_n_words)

    col_nlp1, col_nlp2 = st.columns([3,2], gap="medium")

    with col_nlp1:
        wf_df = pd.DataFrame(word_freq, columns=["Kelime","Frekans"])
        fig_words = go.Figure(go.Bar(
            x=wf_df["Frekans"], y=wf_df["Kelime"],
            orientation="h",
            marker=dict(
                color=wf_df["Frekans"],
                colorscale=[[0,"#7f1d1d"],[0.5,"#ef4444"],[1,"#fca5a5"]],
                showscale=False, line=dict(width=0),
            ),
            text=wf_df["Frekans"], textposition="outside",
            textfont=dict(color="#e2e8f0", size=10),
            hovertemplate="<b>%{y}</b><br>%{x} kez<extra></extra>",
        ))
        _fmt_layout(fig_words, title=f"'{selected_app}' — Negatif Yorumlardaki En Sık Kelimeler",
                    height=520,
                    yaxis=dict(autorange="reversed", gridcolor="rgba(30,58,95,0.6)"),
                    xaxis=dict(title="Frekans", gridcolor="rgba(30,58,95,0.6)"))
        st.plotly_chart(fig_words, use_container_width=True)

    with col_nlp2:
        st.markdown("#### 🔑 Kritik Şikayet Kelimeleri")
        max_freq = wf_df["Frekans"].max() if not wf_df.empty else 1
        for _, row in wf_df.head(15).iterrows():
            pct = row["Frekans"]/max_freq*100
            st.markdown(f"""
<div class="word-row">
  <span style="width:90px;color:#e2e8f0;font-weight:600;font-size:.85rem">{row['Kelime']}</span>
  <div class="word-bar" style="width:{pct:.0f}%;min-width:4px;flex:1"></div>
  <span style="color:#94a3b8;font-size:.82rem;min-width:28px;text-align:right">{row['Frekans']}</span>
</div>
""", unsafe_allow_html=True)

        # Donut
        sent_counts = all_rev["Sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Duygu","Sayı"]
        sent_map = {"Positive":"😊 Pozitif","Negative":"😤 Negatif","Neutral":"😐 Nötr"}
        sent_counts["Duygu"] = sent_counts["Duygu"].map(sent_map).fillna(sent_counts["Duygu"])
        fig_donut = px.pie(sent_counts, names="Duygu", values="Sayı",
                           title="Duygu Dağılımı",
                           color_discrete_sequence=["#34d399","#ef4444","#94a3b8"],
                           hole=0.52)
        fig_donut.update_traces(textfont_size=11, textfont_color="#e2e8f0",
                                 marker=dict(line=dict(color="#04091a", width=2)))
        _fmt_layout(fig_donut, height=280)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Karşılaştırmalı Kelime Analizi
    st.markdown("---")
    st.markdown("#### 🔄 Pozitif vs Negatif Kelime Karşılaştırması")
    col_cmp1, col_cmp2 = st.columns(2, gap="medium")
    with col_cmp1:
        pwf_df = pd.DataFrame(pos_word_freq, columns=["Kelime","Frekans"])
        if not pwf_df.empty:
            fig_pos = go.Figure(go.Bar(
                x=pwf_df["Frekans"][:15], y=pwf_df["Kelime"][:15],
                orientation="h",
                marker=dict(color=pwf_df["Frekans"][:15],
                            colorscale=[[0,"#064e3b"],[1,"#34d399"]],
                            showscale=False, line=dict(width=0)),
                text=pwf_df["Frekans"][:15], textposition="outside",
                textfont=dict(color="#e2e8f0", size=10),
            ))
            _fmt_layout(fig_pos, title="En Sık Pozitif Kelimeler", height=320,
                        yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_pos, use_container_width=True)

    with col_cmp2:
        pol_data = all_rev[all_rev["Sentiment_Polarity"].notna()].copy()
        pol_data["Sentiment_Polarity"] = pd.to_numeric(pol_data["Sentiment_Polarity"], errors="coerce")
        if not pol_data.empty:
            fig_pol = px.histogram(
                pol_data, x="Sentiment_Polarity",
                color="Sentiment", nbins=40, opacity=0.8,
                title="Duygu Polarite Dağılımı",
                labels={"Sentiment_Polarity":"Polarite","count":"Yorum Sayısı","Sentiment":"Duygu"},
                color_discrete_map={"Positive":"#34d399","Negative":"#ef4444","Neutral":"#94a3b8"},
            )
            fig_pol.add_vline(x=0, line_dash="dash", line_color="#f59e0b",
                               annotation_text="Nötr", annotation_font_color="#f59e0b")
            _fmt_layout(fig_pol, height=320)
            st.plotly_chart(fig_pol, use_container_width=True)

    # Örnek yorumlar
    st.markdown("---")
    st.markdown("#### 📝 Örnek Negatif Yorumlar")
    for i, rev in enumerate(neg_reviews[:8], 1):
        st.markdown(f"""
<div class="opp-card" style="border-left-color:#ef4444">
  <p><b>#{i}</b> — {rev[:400]}{"…" if len(rev)>400 else ""}</p>
</div>
""", unsafe_allow_html=True)

    # Actionable insight
    top_complaints = [w for w,_ in word_freq[:5]]
    if top_complaints:
        st.success(
            f"**💡 Girişimci Çıkarımı — {selected_app}:**\n\n"
            f"En sık şikayet edilen konular: **{', '.join(top_complaints)}**. "
            f"Şikayet oranı **{neg_rate:.0f}%** ile {'yüksek' if neg_rate>30 else 'normal'} seviyede. "
            f"Bu sorunları çözen bir uygulama, mevcut mutsuz kullanıcı kitlesini doğrudan hedefleyebilir."
        )

# ─────────────────────────── FOOTER ────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#1e3a5f;font-size:.8rem'>"
    f"AppVentures v2 &nbsp;·&nbsp; {TOTAL_APPS:,} uygulama analiz edildi &nbsp;·&nbsp; "
    f"Kaggle Google Play Store Dataset &nbsp;·&nbsp; Built with Streamlit &amp; Plotly"
    f"</p>",
    unsafe_allow_html=True,
)

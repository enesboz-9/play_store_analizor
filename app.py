"""
AppVentures: Mobil Girişimler İçin Akıllı Pazar Analizi ve Fırsat Radarı
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
st.markdown(
    """
<style>
/* ── Base ── */
html, body, [data-testid="stApp"] {
    background-color: #060d1f;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #38bdf8;
}
/* ── Tabs ── */
[data-testid="stTabs"] button {
    background: transparent !important;
    color: #94a3b8 !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.2rem !important;
    transition: all .2s;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}
/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0f2240 0%, #0a1a35 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 1.1rem 1.3rem !important;
}
[data-testid="stMetricLabel"]  { color: #94a3b8 !important; font-size: .8rem; }
[data-testid="stMetricValue"]  { color: #38bdf8 !important; font-weight: 700; }
[data-testid="stMetricDelta"]  { font-size: .78rem; }
/* ── DataFrames ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
/* ── Headers ── */
h1 { color: #38bdf8 !important; }
h2, h3 { color: #7dd3fc !important; }
/* ── Divider ── */
hr { border-color: #1e3a5f !important; }
/* ── Info / Warning boxes ── */
[data-testid="stAlert"] { border-radius: 10px; }
/* ── Selectbox, Multiselect ── */
.stSelectbox div[data-baseweb], .stMultiSelect div[data-baseweb] {
    background-color: #0f2240 !important;
    border-color: #1e3a5f !important;
    border-radius: 8px !important;
}
/* ── Slider ── */
.stSlider > div { color: #38bdf8; }
/* ── Neon badge ── */
.neon-badge {
    display: inline-block;
    background: rgba(56,189,248,.15);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .05em;
}
/* ── Opportunity card ── */
.opp-card {
    background: linear-gradient(135deg,#0f2240,#0a1a35);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
}
.opp-card h4 { color: #fbbf24; margin:0 0 .3rem 0; }
.opp-card p  { color: #94a3b8; margin:0; font-size:.85rem; }
/* ── Word freq row ── */
.word-row {
    display:flex; align-items:center; gap:1rem;
    padding:.4rem .6rem; border-radius:6px;
    margin-bottom:.3rem;
    background:rgba(15,34,64,.5);
}
.word-bar {
    height:8px; border-radius:4px;
    background: linear-gradient(90deg,#ef4444,#f97316);
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────── DATA LOADING ──────────────────────────────────
import urllib.request
import requests
from pathlib import Path
_BASE = Path(__file__).parent

# Streamlit Cloud'da /tmp klasörü yazılabilir; lokal çalışmada proje klasörü kullanılır
_CACHE_DIR = Path("/tmp") if Path("/tmp").exists() and not Path("/tmp").stat().st_size == 0 else _BASE
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Kaggle'dan doğrudan indirilemez (auth gerekir).
# Hugging Face Hub'da barındırılan açık kopyaları kullanıyoruz.
_REMOTE_URLS = {
    # Büyük CSV → Hugging Face (?download=true endpoint ile xet formatını atla)
    "Google-Playstore.csv": (
        "https://huggingface.co/datasets/enesboz9/google-playstore/resolve/main/Google-Playstore.csv?download=true"
    ),
    # Küçük reviews dosyası → GitHub raw (7MB, GitHub limiti dahilinde)
    "googleplaystore_user_reviews.csv": (
        "https://raw.githubusercontent.com/enesboz-9/play_store_analizor/main/googleplaystore_user_reviews.csv"
    ),
}

def _lfs_pointer(path: Path) -> bool:
    """Git LFS pointer dosyası mı kontrol et (gerçek CSV değil)."""
    try:
        with open(path, "rb") as f:
            header = f.read(50)
        return header.startswith(b"version https://git-lfs")
    except Exception:
        return False

def _find_or_download(*filenames):
    """
    Önce lokal klasörlerde ara. LFS pointer ise veya yoksa /tmp'ye indir.
    """
    search_dirs = [_BASE, _BASE / "data", _CACHE_DIR]

    for filename in filenames:
        for d in search_dirs:
            candidate = d / filename
            if candidate.exists() and not _lfs_pointer(candidate):
                return str(candidate)

    # Lokal yoksa veya LFS pointer ise: indir
    for filename in filenames:
        if filename in _REMOTE_URLS:
            dest = _CACHE_DIR / filename
            url  = _REMOTE_URLS[filename]
            if not dest.exists() or _lfs_pointer(dest):
                st.info(f"⬇️ **{filename}** indiriliyor… (ilk açılışta birkaç dakika sürebilir)")
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    with requests.get(url, headers=headers, stream=True, timeout=300) as r:
                        r.raise_for_status()
                        with open(dest, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    st.success(f"✅ {filename} indirildi.")
                    return str(dest)
                except Exception as e:
                    st.error(
                        f"**{filename} indirilemedi.**\n\n"
                        f"Hata: `{e}`\n\n"
                        f"URL: `{url}`"
                    )
                    raise
            else:
                return str(dest)

    raise FileNotFoundError(
        f"Şu dosyalardan biri bulunamadı ve indirilemedi: {filenames}"
    )

# Yeni veri seti (Google-Playstore.csv) öncelikli; yoksa eski formata düşer
APPS_PATH    = _find_or_download("Google-Playstore.csv", "googleplaystore.csv")
REVIEWS_PATH = _find_or_download("googleplaystore_user_reviews.csv")

# Hangi formatta olduğunu tespit et
_IS_NEW_FORMAT = Path(APPS_PATH).name == "Google-Playstore.csv"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,26,53,0.6)",
    font=dict(color="#e2e8f0", family="Inter"),
    title_font=dict(color="#7dd3fc", size=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e3a5f", borderwidth=1),
    xaxis=dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    colorway=["#38bdf8", "#818cf8", "#34d399", "#f59e0b", "#f472b6",
               "#60a5fa", "#a78bfa", "#4ade80", "#fb923c", "#e879f9"],
    margin=dict(l=10, r=10, t=50, b=10),
)


def _fmt_layout(fig: go.Figure, **extra) -> go.Figure:
    layout = {**PLOTLY_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig


@st.cache_data(show_spinner="Veriler yükleniyor…")
def load_apps() -> pd.DataFrame:
    # ── Büyük veri seti için dtypes önceden belirt (bellek tasarrufu) ──
    if _IS_NEW_FORMAT:
        dtype_hints = {
            "App Name": "str", "App Id": "str", "Category": "str",
            "Rating": "float32", "Rating Count": "float32",
            "Installs": "str", "Minimum Installs": "float32",
            "Maximum Installs": "float32",
            "Free": "str", "Price": "float32", "Currency": "str",
            "Size": "str", "Minimum Android": "str",
            "Content Rating": "str", "Ad Supported": "str",
            "In App Purchases": "str", "Editors Choice": "str",
        }
        df = pd.read_csv(
            APPS_PATH,
            on_bad_lines="skip",
            dtype=dtype_hints,
            low_memory=True,
        )
        # Kolon adlarını eski formata eşle
        df = df.rename(columns={
            "App Name":      "App",
            "Rating Count":  "Reviews",
            "Minimum Installs": "Installs_num_raw",
        })
        # Free sütunu "True"/"False" string → bool
        df["Is_Free"] = df["Free"].astype(str).str.strip().str.lower() == "true"
        df["Price_num"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)

        # Installs: önce Minimum Installs (sayısal), yoksa Installs string
        def parse_installs_new(row):
            v = row.get("Installs_num_raw")
            if pd.notna(v):
                try:
                    return int(float(v))
                except (ValueError, OverflowError):
                    pass
            raw = str(row.get("Installs", "")).replace(",", "").replace("+", "").strip()
            try:
                return int(raw)
            except ValueError:
                return np.nan

        df["Installs_num"] = df.apply(parse_installs_new, axis=1)

    else:
        # ── ESKİ FORMAT (googleplaystore.csv) ──
        df = pd.read_csv(APPS_PATH, on_bad_lines="skip")

        def clean_installs(v):
            if pd.isna(v):
                return np.nan
            v = str(v).replace(",", "").replace("+", "").strip()
            try:
                return int(v)
            except ValueError:
                return np.nan

        df["Installs_num"] = df["Installs"].apply(clean_installs)
        df["Reviews"]      = pd.to_numeric(df["Reviews"], errors="coerce")
        df["Price_num"]    = (
            df["Price"]
            .str.replace(r"[\$,]", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )
        df["Is_Free"] = df["Type"].str.strip() == "Free"

    # ── Ortak temizlik ──
    def clean_size(v):
        if pd.isna(v):
            return np.nan
        v = str(v).strip()
        if "Varies" in v or v in ("", "nan"):
            return np.nan
        if v.endswith("M"):
            try:
                return float(v[:-1])
            except ValueError:
                return np.nan
        if v.endswith("k"):
            try:
                return float(v[:-1]) / 1024
            except ValueError:
                return np.nan
        # Yeni formatta bazı değerler bytes cinsinden gelir (örn. "1.5M" → zaten işlendi)
        try:
            return float(v) / (1024 * 1024)  # bytes → MB
        except ValueError:
            return np.nan

    df["Size_MB"] = df["Size"].apply(clean_size)
    df["Rating"]  = pd.to_numeric(df["Rating"], errors="coerce").astype("float32")

    # Hatalı satırları çıkar
    df = df[df["Rating"].between(1, 5, inclusive="both") | df["Rating"].isna()]
    df = df[df["Category"].notna()]
    df = df[~df["Category"].isin(["1.9"])]  # eski formattaki hatalı satır

    # Kategori adlarını düzenle
    df["Category_Clean"] = (
        df["Category"]
        .str.replace("_", " ", regex=False)
        .str.title()
    )

    # Belleği azalt: büyük veri setinde gereksiz kolonları düşür
    keep_cols = [
        "App", "Category", "Category_Clean", "Rating", "Reviews",
        "Installs_num", "Size_MB", "Is_Free", "Price_num",
        "Content Rating",
    ]
    # Opsiyonel kolonlar (varsa tut)
    for opt in ["Last Updated", "Released", "Editors Choice", "Ad Supported", "In App Purchases"]:
        if opt in df.columns:
            keep_cols.append(opt)

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

# Veri seti bilgi banneri
if _IS_NEW_FORMAT:
    st.sidebar.success(
        f"✅ **Yeni veri seti yüklendi**\n\n"
        f"📱 {len(apps_df):,} uygulama\n\n"
        f"🗂️ {apps_df['Category_Clean'].nunique()} kategori"
    )

# Convenience lookups
ALL_CATS    = sorted(apps_df["Category_Clean"].dropna().unique().tolist())
CAT_MAP     = dict(zip(apps_df["Category_Clean"], apps_df["Category"]))  # display → raw
NEON_COLORS = ["#38bdf8", "#818cf8", "#34d399", "#f59e0b", "#f472b6"]

# ─────────────────────────── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 AppVentures")
    st.markdown(
        "<span class='neon-badge'>B2B Pazar Zekası</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 🔍 Global Filtreler")

    selected_cats = st.multiselect(
        "Kategoriler",
        options=ALL_CATS,
        default=ALL_CATS[:5],
        help="Tüm sekmeleri etkiler",
    )

    min_installs = st.select_slider(
        "Min. İndirme Sayısı",
        options=[0, 100, 1_000, 10_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000],
        value=0,
        format_func=lambda x: f"{x:,}+" if x else "Tümü",
    )

    show_free   = st.checkbox("Ücretsiz Uygulamalar",  value=True)
    show_paid   = st.checkbox("Ücretli Uygulamalar",   value=True)

    st.markdown("---")
    st.markdown("### ⚡ Fırsat Eşikleri")
    opp_min_installs = st.slider(
        "Min İndirme (M)",
        min_value=0.1, max_value=50.0, value=10.0, step=0.5,
        help="Sekme 2: Talep eşiği",
    )
    opp_max_rating = st.slider(
        "Max Puan",
        min_value=3.9, max_value=4.5, value=4.2, step=0.05,
        help="Sekme 2: Memnuniyet eşiği",
    )

    st.markdown("---")
    st.caption("Veri: Kaggle Google Play Store Dataset")
    if _IS_NEW_FORMAT:
        st.caption("📅 Analiz Dönemi: 2021 · ~2.3M uygulama")
    else:
        st.caption("📅 Analiz Dönemi: 2019")


# ─────────────────────────── FILTER HELPER ─────────────────────────────────
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    cats = selected_cats if selected_cats else ALL_CATS
    mask = df["Category_Clean"].isin(cats)
    if min_installs:
        mask &= df["Installs_num"] >= min_installs
    type_mask = pd.Series([False] * len(df), index=df.index)
    if show_free:
        type_mask |= df["Is_Free"]
    if show_paid:
        type_mask |= ~df["Is_Free"]
    return df[mask & type_mask]


filtered_df = apply_filters(apps_df)

# ─────────────────────────── HEADER ────────────────────────────────────────
st.markdown(
    """
<div style="padding:1.5rem 0 .5rem 0">
  <h1 style="margin:0;font-size:2rem;letter-spacing:-.02em">
    🚀 AppVentures
  </h1>
  <p style="color:#64748b;margin:.2rem 0 0 0;font-size:1rem">
    Mobil Girişimler İçin Akıllı Pazar Analizi &amp; Fırsat Radarı
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────── KPI STRIP ─────────────────────────────────────
# ─────────────────────────── KPI STRIP ─────────────────────────────────────
kc = st.columns(5)
kc[0].metric("📱 Toplam Uygulama",    f"{len(filtered_df):,}")
kc[1].metric("⭐ Ort. Puan",          f"{filtered_df['Rating'].mean():.2f}")
median_inst = filtered_df["Installs_num"].median()
kc[2].metric("📥 Medyan İndirme",     f"{int(median_inst):,}" if pd.notna(median_inst) else "—")
kc[3].metric("🆓 Ücretsiz Oran",      f"{filtered_df['Is_Free'].mean()*100:.0f}%")
kc[4].metric("🗂️ Kategori Sayısı",    f"{filtered_df['Category_Clean'].nunique()}")

st.markdown("---")

# ─────────────────────────── TABS ──────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔬 Pazarın Röntgeni",
    "🎯 Fırsat Radarı",
    "💬 Kullanıcı Ne İstiyor?",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PAZARIn RÖNTGENİ
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if filtered_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı.")
        st.stop()

    st.markdown("### 🏭 Rekabet Yoğunluğu")
    st.caption("Kategorilere göre uygulama sayısı ve ortalama puan dağılımı")

    # ── App count per category (bubble) ──
    cat_agg = (
        filtered_df
        .groupby("Category_Clean", as_index=False)
        .agg(
            app_count     =("App",          "count"),
            avg_rating    =("Rating",        "mean"),
            total_installs=("Installs_num",  "sum"),
            free_pct      =("Is_Free",       "mean"),
        )
        .sort_values("total_installs", ascending=False)
    )
    cat_agg["avg_rating"]     = cat_agg["avg_rating"].round(2)
    cat_agg["total_installs_M"] = (cat_agg["total_installs"] / 1e6).round(1)
    cat_agg["free_pct_label"]   = (cat_agg["free_pct"] * 100).round(0).astype(int).astype(str) + "%"

    col_a, col_b = st.columns([3, 2], gap="medium")

    with col_a:
        fig_bubble = px.scatter(
            cat_agg,
            x="avg_rating",
            y="app_count",
            size="total_installs_M",
            color="Category_Clean",
            hover_name="Category_Clean",
            hover_data={
                "avg_rating": ":.2f",
                "app_count": True,
                "total_installs_M": ":.1f",
                "Category_Clean": False,
            },
            labels={
                "avg_rating": "Ort. Puan",
                "app_count": "Uygulama Sayısı",
                "total_installs_M": "Toplam İndirme (M)",
            },
            title="Kategori Haritası: Rekabet × Puan × İndirme",
            size_max=55,
        )
        _fmt_layout(fig_bubble)
        fig_bubble.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="#0a1628")))
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_b:
        top10 = cat_agg.nlargest(10, "app_count").sort_values("app_count")
        fig_bar = go.Figure(go.Bar(
            y=top10["Category_Clean"],
            x=top10["app_count"],
            orientation="h",
            marker=dict(
                color=top10["avg_rating"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
                showscale=True,
                colorbar=dict(title="Ort. Puan", tickfont=dict(color="#94a3b8")),
                line=dict(width=0),
            ),
            text=top10["app_count"],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
            hovertemplate="<b>%{y}</b><br>%{x} uygulama<extra></extra>",
        ))
        _fmt_layout(fig_bar, title="En Kalabalık 10 Kategori")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💰 Fiyatlandırma Modeli Analizi")
    st.caption("Ücretsiz vs Ücretli — indirilme ve puan farkları")

    price_agg = (
        filtered_df
        .groupby(["Category_Clean", "Is_Free"], as_index=False)
        .agg(count=("App","count"), avg_rating=("Rating","mean"),
             avg_installs=("Installs_num","mean"))
    )
    price_agg["Model"]         = price_agg["Is_Free"].map({True:"Ücretsiz", False:"Ücretli"})
    price_agg["avg_installs_k"] = (price_agg["avg_installs"] / 1e3).round(1)

    col_c, col_d = st.columns(2, gap="medium")

    with col_c:
        fig_pie_data = (
            filtered_df
            .groupby("Is_Free")["App"]
            .count()
            .reset_index()
        )
        fig_pie_data["Label"] = fig_pie_data["Is_Free"].map({True:"Ücretsiz 🆓", False:"Ücretli 💎"})
        fig_pie = px.pie(
            fig_pie_data, names="Label", values="App",
            title="Uygulama Dağılımı (Ücretsiz / Ücretli)",
            color_discrete_sequence=["#38bdf8", "#f59e0b"],
            hole=0.45,
        )
        fig_pie.update_traces(textfont_size=13, textfont_color="#e2e8f0",
                               marker=dict(line=dict(color="#060d1f", width=3)))
        _fmt_layout(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_d:
        fig_violin = px.violin(
            filtered_df[filtered_df["Rating"].notna()],
            x="Is_Free", y="Rating",
            color="Is_Free",
            color_discrete_map={True:"#38bdf8", False:"#f59e0b"},
            labels={"Is_Free": "Model", "Rating": "Puan"},
            category_orders={"Is_Free": [True, False]},
            title="Puan Dağılımı: Ücretsiz vs Ücretli",
            box=True, points="suspectedoutliers",
        )
        fig_violin.update_layout(
            xaxis=dict(
                tickvals=[True, False],
                ticktext=["Ücretsiz", "Ücretli"],
            ),
            showlegend=False,
        )
        _fmt_layout(fig_violin)
        st.plotly_chart(fig_violin, use_container_width=True)

    # ── Strategy insight cards ──
    st.markdown("### 🧭 Strateji Önerileri")
    free_avg   = filtered_df[filtered_df["Is_Free"]]["Rating"].mean()
    paid_avg   = filtered_df[~filtered_df["Is_Free"]]["Rating"].mean()
    free_inst  = filtered_df[filtered_df["Is_Free"]]["Installs_num"].median()
    paid_inst  = filtered_df[~filtered_df["Is_Free"]]["Installs_num"].median()

    si1, si2, si3 = st.columns(3, gap="medium")
    with si1:
        winner = "Ücretsiz" if free_inst > paid_inst else "Ücretli"
        ratio  = max(free_inst, paid_inst) / (min(free_inst, paid_inst) + 1)
        st.info(
            f"**📈 Büyüme Taktiği**\n\n"
            f"{winner} model, medyan indirme açısından "
            f"**{ratio:.1f}× daha fazla** erişim sağlıyor. "
            f"Kullanıcı tabanını hızla büyütmek için ücretsiz/freemium başlayın."
        )
    with si2:
        better = "Ücretli" if paid_avg > free_avg else "Ücretsiz"
        diff   = abs(paid_avg - free_avg)
        st.success(
            f"**⭐ Kalite Sinyali**\n\n"
            f"{better} uygulamalar ortalamada "
            f"**{diff:.2f} puan** daha yüksek skorluyor. "
            f"Premium segmentte kullanıcı tatminini ön plana çıkarın."
        )
    with si3:
        top_cat = cat_agg.nlargest(1, "total_installs_M")["Category_Clean"].values[0]
        st.warning(
            f"**🏆 Lider Kategori**\n\n"
            f"**{top_cat}** kategorisi en fazla indirmeyi çekiyor. "
            f"Bu alanda farklılaşan bir niş bulmak veya bu kategoriye "
            f"entegre bir araç geliştirmek yüksek potansiyel taşıyor."
        )

    st.markdown("---")
    st.markdown("### 📊 İndirme Trendi — Kategori Karşılaştırması")

    inst_cat = (
        filtered_df
        .groupby("Category_Clean")["Installs_num"]
        .agg(["sum","median","mean"])
        .reset_index()
        .rename(columns={"sum":"Toplam","median":"Medyan","mean":"Ortalama"})
        .sort_values("Toplam", ascending=False)
        .head(15)
    )
    inst_cat_m = inst_cat.melt(
        id_vars="Category_Clean",
        value_vars=["Toplam","Medyan","Ortalama"],
        var_name="Metrik", value_name="İndirme",
    )
    fig_grouped = px.bar(
        inst_cat_m,
        x="Category_Clean", y="İndirme", color="Metrik",
        barmode="group",
        title="İndirme İstatistikleri (İlk 15 Kategori)",
        labels={"Category_Clean":"Kategori","İndirme":"İndirme Sayısı"},
        color_discrete_sequence=["#38bdf8","#f59e0b","#34d399"],
    )
    fig_grouped.update_layout(xaxis_tickangle=-35)
    _fmt_layout(fig_grouped)
    st.plotly_chart(fig_grouped, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FIRSAT RADARI
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🎯 Fırsat Algoritması")
    st.markdown(
        f"> Yüksek talep **(>{opp_min_installs:.1f}M indirme)** "
        f"ama düşük memnuniyet **(<{opp_max_rating} puan)** olan alanlar. "
        f"Girişimci için altın bölge."
    )

    opp_threshold_inst = opp_min_installs * 1_000_000

    # Per-app opportunity check
    opp_apps = filtered_df[
        (filtered_df["Installs_num"] >= opp_threshold_inst) &
        (filtered_df["Rating"] <= opp_max_rating) &
        filtered_df["Rating"].notna()
    ].copy()

    # Per-category opportunity
    cat_opp = (
        filtered_df
        .groupby("Category_Clean", as_index=False)
        .agg(
            app_count      =("App",          "count"),
            avg_rating     =("Rating",        "mean"),
            total_installs =("Installs_num",  "sum"),
            high_inst_apps =("Installs_num",  lambda x: (x >= opp_threshold_inst).sum()),
        )
    )
    cat_opp["avg_rating"] = cat_opp["avg_rating"].round(2)
    cat_opp["total_M"]    = (cat_opp["total_installs"] / 1e6).round(1)

    # Opportunity score: demand / satisfaction
    cat_opp["opp_score"] = (
        cat_opp["total_M"] / (cat_opp["avg_rating"].clip(lower=0.1))
    ).round(1)

    cat_opp_filtered = cat_opp[
        (cat_opp["total_M"] >= opp_min_installs) &
        (cat_opp["avg_rating"] <= opp_max_rating)
    ].sort_values("opp_score", ascending=False)

    st.markdown(f"**{len(cat_opp_filtered)} kategori** bu kriterleri karşılıyor.")

    # ── Quadrant chart ──
    fig_quad = go.Figure()

    # Background quadrants
    x_mid = opp_max_rating
    fig_quad.add_shape(type="rect", x0=1, y0=opp_threshold_inst/1e6,
                        x1=x_mid, y1=filtered_df["Installs_num"].max()/1e6 * 1.1,
                        fillcolor="rgba(239,68,68,0.08)", line_width=0)
    fig_quad.add_annotation(x=2.4, y=filtered_df["Installs_num"].max()/1e6 * 0.85,
                             text="🔥 FIRSAT BÖLGESİ", showarrow=False,
                             font=dict(color="#f87171", size=12, family="Inter"))

    # All categories
    fig_quad.add_trace(go.Scatter(
        x=cat_opp["avg_rating"],
        y=cat_opp["total_M"],
        mode="markers+text",
        text=cat_opp["Category_Clean"].str.split().str[0],
        textposition="top center",
        textfont=dict(size=9, color="#94a3b8"),
        marker=dict(
            size=cat_opp["opp_score"].clip(upper=500) / 10 + 8,
            color=cat_opp["avg_rating"],
            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#34d399"]],
            showscale=True,
            colorbar=dict(title="Puan", tickfont=dict(color="#94a3b8")),
            opacity=0.85,
            line=dict(color="#0a1628", width=1),
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Ort. Puan: %{x:.2f}<br>"
            "Toplam İndirme: %{y:.1f}M<br>"
            "Fırsat Skoru: %{customdata[1]:.0f}<extra></extra>"
        ),
        customdata=np.stack([cat_opp["Category_Clean"], cat_opp["opp_score"]], axis=1),
        name="Kategori",
    ))

    # Reference lines
    fig_quad.add_vline(x=opp_max_rating, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"Puan eşiği: {opp_max_rating}",
                        annotation_font_color="#f59e0b")
    fig_quad.add_hline(y=opp_min_installs, line_dash="dash", line_color="#38bdf8",
                        annotation_text=f"{opp_min_installs}M İndirme",
                        annotation_font_color="#38bdf8")

    _fmt_layout(fig_quad,
                title="Talep × Memnuniyet Matrisi (Fırsat Haritası)",
                xaxis=dict(title="Ortalama Kullanıcı Puanı", range=[1,5],
                           gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
                yaxis=dict(title="Toplam İndirme (Milyon)", type="log",
                           gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
                height=500)
    st.plotly_chart(fig_quad, use_container_width=True)

    # ── Opportunity cards ──
    if cat_opp_filtered.empty:
        st.info("Mevcut filtreler ile fırsat bulunamadı. Eşikleri gevşetin.")
    else:
        st.markdown("### 💡 Tespit Edilen Fırsatlar")
        for _, row in cat_opp_filtered.iterrows():
            demand_level = "🔥 Çok Yüksek" if row["total_M"] > 10 else ("⚡ Yüksek" if row["total_M"] > 1 else "📈 Orta")
            sat_level    = "😤 Çok Düşük" if row["avg_rating"] < 3.0 else ("😐 Düşük" if row["avg_rating"] < 3.5 else "😕 Orta-Altı")
            st.markdown(
                f"""
<div class="opp-card">
  <h4>🎯 {row["Category_Clean"]} &nbsp;
    <span class="neon-badge">Fırsat Skoru: {row["opp_score"]:.0f}</span>
  </h4>
  <p>
    📥 <b>{row["total_M"]:.1f}M</b> toplam indirme &nbsp;|&nbsp;
    ⭐ Ort. puan <b>{row["avg_rating"]:.2f}</b> &nbsp;|&nbsp;
    📱 <b>{row["app_count"]}</b> uygulama<br>
    Talep: {demand_level} &nbsp;•&nbsp; Memnuniyet: {sat_level}<br>
    👉 <em>Bu kategoride kullanıcılar fazla — ama memnun değil. 
    Rakiplerin eksikliklerini kapatın, pazar payı kapın.</em>
  </p>
</div>
""",
                unsafe_allow_html=True,
            )

    # ── Opportunity apps table ──
    st.markdown("---")
    st.markdown(f"### 📋 Fırsat Uygulamaları Tablosu")
    st.caption(
        f">{opp_min_installs:.1f}M indirme ve <{opp_max_rating} puan olan bireysel uygulamalar"
    )

    if opp_apps.empty:
        st.info("Bu kriterleri karşılayan uygulama bulunamadı.")
    else:
        display_cols = ["App","Category_Clean","Rating","Installs_num","Is_Free","Reviews"]
        opp_show = (
            opp_apps[display_cols]
            .rename(columns={
                "Category_Clean":"Kategori",
                "Rating":"Puan",
                "Installs_num":"İndirme",
                "Is_Free":"Ücretsiz",
                "Reviews":"Değerlendirme Sayısı",
            })
            .sort_values("İndirme", ascending=False)
            .reset_index(drop=True)
        )
        opp_show["İndirme"] = opp_show["İndirme"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        opp_show["Değerlendirme Sayısı"] = opp_show["Değerlendirme Sayısı"].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else "—"
        )
        opp_show["Ücretsiz"] = opp_show["Ücretsiz"].map({True:"✅ Ücretsiz", False:"💎 Ücretli"})
        st.dataframe(
            opp_show,
            use_container_width=True,
            height=350,
            hide_index=True,
        )

        # ── Rating distribution of opportunity apps ──
        fig_opp_dist = px.histogram(
            opp_apps, x="Rating", nbins=20,
            color="Category_Clean",
            title="Fırsat Uygulamalarının Puan Dağılımı",
            labels={"Rating":"Puan", "count":"Uygulama Sayısı"},
            opacity=0.8,
        )
        _fmt_layout(fig_opp_dist)
        st.plotly_chart(fig_opp_dist, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — KULLANICI NE İSTİYOR?
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 💬 Rakip Uygulama Zayıflık Analizi")
    st.caption(
        "Bir rakip seçin — sistem negatif yorumları analiz ederek teknik "
        "zafiyetleri ve kullanıcı şikayetlerini ortaya çıkarır."
    )

    # Apps that appear in both datasets
    reviewed_apps = sorted(
        reviews_df[reviews_df["Sentiment"] == "Negative"]["App"].unique().tolist()
    )
    # Filter to only apps also in filtered_df (soft filter, fallback to all)
    filtered_app_names = filtered_df["App"].unique().tolist()
    reviewed_and_filtered = [a for a in reviewed_apps if a in filtered_app_names]
    app_pool = reviewed_and_filtered if reviewed_and_filtered else reviewed_apps

    if not app_pool:
        st.warning("Seçilen filtrelerle eşleşen yorumlu uygulama bulunamadı.")
        st.stop()

    selected_app = st.selectbox(
        "🔎 Analiz Edilecek Rakip Uygulama",
        options=app_pool,
        index=0,
        help="Sadece negatif yorumu olan uygulamalar listeleniyor",
    )

    neg_reviews = reviews_df[
        (reviews_df["App"] == selected_app) &
        (reviews_df["Sentiment"] == "Negative")
    ]["Translated_Review"].dropna().tolist()

    pos_reviews = reviews_df[
        (reviews_df["App"] == selected_app) &
        (reviews_df["Sentiment"] == "Positive")
    ]["Translated_Review"].dropna().tolist()

    all_rev = reviews_df[reviews_df["App"] == selected_app]
    total_reviews = len(all_rev)

    if not neg_reviews:
        st.info(f"**{selected_app}** için negatif yorum bulunamadı.")
        st.stop()

    # ── App summary metrics ──
    app_info = apps_df[apps_df["App"] == selected_app].iloc[0] if selected_app in apps_df["App"].values else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🔴 Negatif Yorum",  len(neg_reviews))
    m2.metric("🟢 Pozitif Yorum",  len(pos_reviews))
    m3.metric("📊 Toplam Yorum",   total_reviews)
    neg_rate = len(neg_reviews) / total_reviews * 100 if total_reviews else 0
    m4.metric("⚠️ Şikayet Oranı",  f"{neg_rate:.1f}%",
              delta="yüksek" if neg_rate > 30 else "normal",
              delta_color="inverse")

    if app_info is not None:
        st.markdown(
            f"**Kategori:** {app_info.get('Category_Clean','—')} &nbsp;|&nbsp; "
            f"**Puan:** {app_info.get('Rating','—')} ⭐ &nbsp;|&nbsp; "
            f"**İndirme:** {app_info.get('Installs','—')} &nbsp;|&nbsp; "
            f"**Tip:** {'🆓 Ücretsiz' if app_info.get('Is_Free') else '💎 Ücretli'}"
        )

    st.markdown("---")

    # ── NLP: word frequency ──
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
        "am","im","ive","id","its","thats","youre","theyre","theyre",
    }

    def extract_words(reviews):
        text = " ".join(reviews).lower()
        words = re.findall(r"\b[a-z]{3,}\b", text)
        return [w for w in words if w not in STOPWORDS]

    neg_words = extract_words(neg_reviews)
    word_freq = Counter(neg_words).most_common(30)

    if not word_freq:
        st.warning("Yorum metinlerinden kelime çıkarılamadı.")
        st.stop()

    col_nlp1, col_nlp2 = st.columns([3, 2], gap="medium")

    with col_nlp1:
        wf_df = pd.DataFrame(word_freq, columns=["Kelime", "Frekans"])

        fig_words = go.Figure(go.Bar(
            x=wf_df["Frekans"],
            y=wf_df["Kelime"],
            orientation="h",
            marker=dict(
                color=wf_df["Frekans"],
                colorscale=[[0,"#7f1d1d"],[0.5,"#ef4444"],[1,"#fca5a5"]],
                showscale=False,
                line=dict(width=0),
            ),
            text=wf_df["Frekans"],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=10),
            hovertemplate="<b>%{y}</b><br>%{x} kez geçiyor<extra></extra>",
        ))
        _fmt_layout(
            fig_words,
            title=f"'{selected_app}' — Negatif Yorumlardaki En Sık Kelimeler",
            height=500,
            yaxis=dict(autorange="reversed", gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
            xaxis=dict(title="Frekans", gridcolor="#1e3a5f", zerolinecolor="#1e3a5f"),
        )
        st.plotly_chart(fig_words, use_container_width=True)

    with col_nlp2:
        st.markdown("#### 🔑 En Kritik Şikayetler")
        st.caption("Negatif yorumlardan çıkarılan teknik ve deneyimsel zafiyetler")

        max_freq = wf_df["Frekans"].max()
        for _, row in wf_df.head(12).iterrows():
            pct = row["Frekans"] / max_freq * 100
            st.markdown(
                f"""
<div class="word-row">
  <span style="width:100px;color:#e2e8f0;font-weight:600">{row["Kelime"]}</span>
  <div class="word-bar" style="width:{pct:.0f}%;min-width:4px;flex:1"></div>
  <span style="color:#94a3b8;font-size:.85rem;min-width:30px;text-align:right">
    {row["Frekans"]}
  </span>
</div>
""",
                unsafe_allow_html=True,
            )

        # Sentiment breakdown donut
        sent_counts = all_rev["Sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Duygu", "Sayı"]
        sent_map = {"Positive":"😊 Pozitif","Negative":"😤 Negatif","Neutral":"😐 Nötr"}
        sent_counts["Duygu"] = sent_counts["Duygu"].map(sent_map).fillna(sent_counts["Duygu"])

        fig_donut = px.pie(
            sent_counts, names="Duygu", values="Sayı",
            title="Duygu Dağılımı",
            color_discrete_sequence=["#34d399","#ef4444","#94a3b8"],
            hole=0.5,
        )
        fig_donut.update_traces(
            textfont_size=11, textfont_color="#e2e8f0",
            marker=dict(line=dict(color="#060d1f", width=2))
        )
        _fmt_layout(fig_donut, height=280)
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Polarity timeline ──
    st.markdown("---")
    st.markdown("#### 📉 Duygu Polaritesi Dağılımı")

    pol_data = all_rev[all_rev["Sentiment_Polarity"].notna()].copy()
    pol_data["Sentiment_Polarity"] = pd.to_numeric(pol_data["Sentiment_Polarity"], errors="coerce")

    if not pol_data.empty:
        fig_pol = px.histogram(
            pol_data, x="Sentiment_Polarity",
            color="Sentiment",
            nbins=40, opacity=0.8,
            title=f"{selected_app} — Yorum Polarite Dağılımı (-1: Çok Negatif → +1: Çok Pozitif)",
            labels={"Sentiment_Polarity":"Polarite", "count":"Yorum Sayısı","Sentiment":"Duygu"},
            color_discrete_map={"Positive":"#34d399","Negative":"#ef4444","Neutral":"#94a3b8"},
        )
        fig_pol.add_vline(x=0, line_dash="dash", line_color="#f59e0b",
                           annotation_text="Nötr", annotation_font_color="#f59e0b")
        _fmt_layout(fig_pol)
        st.plotly_chart(fig_pol, use_container_width=True)

    # ── Sample negative reviews ──
    st.markdown("#### 📝 Örnek Negatif Yorumlar")
    sample_n = min(5, len(neg_reviews))
    for i, rev in enumerate(neg_reviews[:sample_n], 1):
        st.markdown(
            f"""
<div class="opp-card" style="border-left-color:#ef4444">
  <p><b>#{i}</b> — {rev[:300]}{"…" if len(rev) > 300 else ""}</p>
</div>
""",
            unsafe_allow_html=True,
        )

    # ── Actionable insight ──
    top_complaints = [w for w, _ in word_freq[:5]]
    st.success(
        f"**💡 Girişimci Çıkarımı — {selected_app}:**\n\n"
        f"Kullanıcıların en çok şikayet ettiği kelimeler: "
        f"**{', '.join(top_complaints)}**. "
        f"Bu sorunları çözen bir uygulama geliştirmek, "
        f"{neg_rate:.0f}% şikayet oranıyla zaten mutsuz olan "
        f"mevcut kullanıcı kitlesini doğrudan hedefleyebilir."
    )

# ─────────────────────────── FOOTER ────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#334155;font-size:.8rem'>"
    "AppVentures &nbsp;·&nbsp; Kaggle Google Play Store Dataset (2021) &nbsp;·&nbsp; "
    "Built with Streamlit &amp; Plotly"
    "</p>",
    unsafe_allow_html=True,
)

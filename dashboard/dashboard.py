from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")

BASE = Path(__file__).parent
ORANGE, BLUE, GREY, LIGHT = "#d95f02", "#1b7a9c", "#bdbdbd", "#9ecae1"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
WEATHER_ORDER = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]


@st.cache_data
def load_data():
    hour = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    day = pd.read_csv(BASE / "day_data.csv", parse_dates=["dteday"])
    day["temp_bin"] = pd.Categorical(day["temp_bin"], ["<10 °C", "10-20 °C", "20-30 °C", ">30 °C"], ordered=True)
    day["demand_level"] = pd.Categorical(day["demand_level"], ["Rendah", "Sedang", "Tinggi"], ordered=True)
    return hour, day


hour_df, day_df = load_data()

# ---------------- Sidebar (filter) ----------------
with st.sidebar:
    st.title("🚲 Filter")
    min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
    date_range = st.date_input("Rentang tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    seasons = st.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
    weathers = st.multiselect("Kondisi cuaca", WEATHER_ORDER + ["Hujan/Salju Lebat"],
                              default=WEATHER_ORDER + ["Hujan/Salju Lebat"])
    st.caption("Sumber: Capital Bikeshare, Washington D.C. (2011–2012)")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = pd.Timestamp(min_d), pd.Timestamp(max_d)


def apply_filter(df):
    return df[(df["dteday"].between(start, end)) & (df["season_label"].isin(seasons))
              & (df["weather_label"].isin(weathers))]


day_f, hour_f = apply_filter(day_df), apply_filter(hour_df)

st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown("Pola permintaan penyewaan sepeda berdasarkan **jam**, **cuaca/musim**, dan **pertumbuhan bulanan**.")

if day_f.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan ubah filter.")
    st.stop()

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{day_f['cnt'].sum():,.0f}")
c2.metric("Rata-rata per hari", f"{day_f['cnt'].mean():,.0f}")
c3.metric("Pengguna registered", f"{day_f['registered'].sum() / day_f['cnt'].sum() * 100:.1f}%")
c4.metric("Pengguna casual", f"{day_f['casual'].sum() / day_f['cnt'].sum() * 100:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["⏰ Pola Jam", "🌦️ Cuaca & Musim", "📈 Pertumbuhan Bulanan", "🧩 Segmentasi"])

# ---------------- Tab 1: Pola jam ----------------
with tab1:
    st.subheader("Kapan permintaan memuncak: hari kerja vs akhir pekan/libur?")
    pattern = hour_f.groupby(["day_type", "hr"])["cnt"].mean().unstack(0)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for t, col in {"Hari Kerja": ORANGE, "Akhir Pekan/Libur": BLUE}.items():
        if t in pattern:
            s = pattern[t].dropna()
            ax.plot(s.index, s.values, marker="o", ms=4, lw=2.5, color=col, label=t)
            top = s.idxmax()
            ax.annotate(f"Puncak {top}:00 ({s.max():.0f})", xy=(top, s.max()),
                        xytext=(top + 0.7, s.max() + 35), color=col, fontweight="bold", fontsize=10)
    ax.axvspan(7, 9.99, color=ORANGE, alpha=0.07)
    ax.axvspan(16, 19.99, color=ORANGE, alpha=0.07)
    ax.set_xticks(range(24))
    ax.set_xlabel("Jam dalam sehari")
    ax.set_ylabel("Rata-rata sepeda disewa per jam")
    ax.legend(frameon=False)
    sns.despine()
    st.pyplot(fig)

    wk = hour_f[hour_f["workingday"] == 1].groupby("hr")["cnt"].mean()
    if not wk.empty:
        peak = [h for h in (7, 8, 9, 16, 17, 18, 19) if h in wk.index]
        st.info(f"Pada hari kerja (sesuai filter), jam sibuk 07–09 & 16–19 menyumbang "
                f"**{wk.loc[peak].sum() / wk.sum() * 100:.1f}%** penyewaan harian. "
                f"Jendela paling sepi: sekitar **{int(wk.idxmin()):02d}.00**, cocok untuk redistribusi/pemeliharaan.")

# ---------------- Tab 2: Cuaca & musim ----------------
with tab2:
    st.subheader("Seberapa besar cuaca menurunkan penyewaan?")
    col_a, col_b = st.columns([1, 1.4])
    avg_w = day_f.groupby("weather_label")["cnt"].mean().reindex(WEATHER_ORDER).dropna()
    with col_a:
        fig, ax = plt.subplots(figsize=(5.5, 4.4))
        colors = [GREY if w != "Hujan/Salju Ringan" else ORANGE for w in avg_w.index]
        bars = ax.bar(avg_w.index, avg_w.values, color=colors, width=0.6)
        base = avg_w.get("Cerah")
        for b, (w, v) in zip(bars, avg_w.items()):
            label = f"{v:,.0f}"
            if base and w != "Cerah":
                label += f"\n({(v / base - 1) * 100:+.0f}%)"
            ax.text(b.get_x() + b.get_width() / 2, v + avg_w.max() * 0.02, label, ha="center", fontweight="bold", fontsize=9)
        ax.set_ylim(0, avg_w.max() * 1.2)
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.tick_params(axis="x", labelsize=8)
        sns.despine()
        st.pyplot(fig)
    with col_b:
        pv = (day_f.pivot_table(index="season_label", columns="weather_label", values="cnt", aggfunc="mean")
              .reindex(index=[s for s in SEASON_ORDER if s in day_f["season_label"].unique()]))
        cols = [w for w in WEATHER_ORDER if w in pv.columns]
        fig, ax = plt.subplots(figsize=(7.5, 4.4))
        pv[cols].plot(kind="bar", ax=ax, color=[BLUE, LIGHT, ORANGE][:len(cols)], width=0.8, rot=0)
        ax.set_xlabel("")
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.legend(title="", frameon=False, fontsize=9)
        sns.despine()
        st.pyplot(fig)

    users = day_f.groupby("weather_label")[["casual", "registered"]].mean().reindex(WEATHER_ORDER).dropna()
    if "Cerah" in users.index and len(users) > 1:
        drop = (1 - users / users.loc["Cerah"]) * 100
        st.markdown("**Penurunan dibanding cuaca cerah (%)**")
        st.dataframe(drop.drop("Cerah").round(1).rename(columns={"casual": "Casual", "registered": "Registered"}))
    st.caption("Catatan: jumlah hari bercuaca hujan/salju ringan sedikit (21 hari pada data penuh), sehingga angka per musim bersifat indikatif.")

# ---------------- Tab 3: Pertumbuhan bulanan ----------------
with tab3:
    st.subheader("Pertumbuhan penyewaan bulanan 2012 vs 2011")
    full = day_df[day_df["season_label"].isin(seasons) & day_df["weather_label"].isin(weathers)]
    monthly = full.groupby(["mnth", "year"])["cnt"].sum().unstack().reindex(range(1, 13))
    if {2011, 2012} <= set(monthly.columns):
        monthly["growth"] = (monthly[2012] / monthly[2011] - 1) * 100
        monthly.index = MONTHS
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1.5, 1]})
        ax[0].plot(MONTHS, monthly[2011], marker="o", lw=2.5, color=GREY, label="2011")
        ax[0].plot(MONTHS, monthly[2012], marker="o", lw=2.5, color=BLUE, label="2012")
        ax[0].set_ylabel("Total penyewaan per bulan")
        ax[0].legend(frameon=False)
        g = monthly["growth"].dropna()
        low = g.idxmin()
        ax[1].bar(g.index, g.values, color=[ORANGE if m == low else GREY for m in g.index])
        ax[1].set_title("Pertumbuhan YoY (%)", loc="left", fontweight="bold")
        ax[1].tick_params(axis="x", labelsize=8)
        ax[1].text(g.index.get_loc(low), g[low] + 3, f"Terendah: {low}\n{g[low]:.0f}%", ha="center",
                   color=ORANGE, fontweight="bold", fontsize=9)
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
        tot = monthly[2012].sum() / monthly[2011].sum() - 1
        st.info(f"Total penyewaan 2012 tumbuh **{tot * 100:.1f}%** dibanding 2011 (berdasarkan filter musim & cuaca; "
                f"filter tanggal tidak berlaku di tab ini karena membandingkan dua tahun penuh).")
    else:
        st.warning("Pilih filter yang mencakup data 2011 dan 2012 untuk melihat pertumbuhan.")

# ---------------- Tab 4: Segmentasi (manual grouping & binning) ----------------
with tab4:
    st.subheader("Analisis lanjutan: manual grouping & binning")
    c_a, c_b, c_c = st.columns(3)
    seg_order = ["Dini Hari (00-05)", "Sibuk Pagi (06-09)", "Siang (10-15)", "Sibuk Sore (16-19)", "Malam (20-23)"]
    seg = hour_f.pivot_table(index="time_segment", columns="day_type", values="cnt", aggfunc="mean").reindex(seg_order)
    with c_a:
        st.markdown("**Segmen waktu**")
        fig, ax = plt.subplots(figsize=(5, 4.4))
        seg.plot(kind="bar", ax=ax, color=[ORANGE if c == "Hari Kerja" else BLUE for c in seg.columns], rot=35, width=0.75)
        ax.set_xlabel("")
        ax.legend(frameon=False, fontsize=8)
        sns.despine()
        st.pyplot(fig)
    with c_b:
        st.markdown("**Rentang suhu**")
        t = day_f.groupby("temp_bin", observed=True)["cnt"].mean()
        fig, ax = plt.subplots(figsize=(5, 4.4))
        best = t.idxmax()
        ax.bar(t.index.astype(str), t.values, color=[BLUE if i == best else GREY for i in t.index])
        for i, v in enumerate(t.values):
            ax.text(i, v + t.max() * 0.02, f"{v:,.0f}", ha="center", fontweight="bold", fontsize=9)
        ax.set_ylabel("Rata-rata penyewaan harian")
        sns.despine()
        st.pyplot(fig)
    with c_c:
        st.markdown("**Tingkat permintaan per musim (%)**")
        dem = pd.crosstab(day_f["season_label"], day_f["demand_level"], normalize="index") * 100
        dem = dem.reindex([s for s in SEASON_ORDER if s in dem.index])
        fig, ax = plt.subplots(figsize=(5, 4.4))
        dem.plot(kind="bar", stacked=True, ax=ax, color=[GREY, LIGHT, BLUE][:dem.shape[1]], rot=0, width=0.7)
        ax.set_xlabel("")
        ax.legend(title="", frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)
        sns.despine()
        st.pyplot(fig)
    st.caption("Tingkat permintaan: Rendah < 3.000, Sedang 3.000–5.999, Tinggi ≥ 6.000 sepeda/hari.")

st.divider()
st.markdown("### Rekomendasi")
st.markdown(
    "- **Redistribusi & pemeliharaan:** siapkan sepeda di stasiun komuter sebelum 07.00 dan 16.00 pada hari kerja; "
    "lakukan pemeliharaan pada 02.00–05.00.\n"
    "- **Cuaca buruk:** kurangi sebaran armada saat hujan ringan dan beri insentif untuk pengguna *casual* yang paling terdampak.\n"
    "- **Promosi:** fokuskan kampanye pada bulan berpertumbuhan terendah (Juni, Desember) dan bulan dingin bervolume rendah."
)
st.caption("Dashboard dibuat untuk Proyek Analisis Data – Bike Sharing Dataset.")

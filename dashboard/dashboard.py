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
PEAK_HOURS = [7, 8, 9, 16, 17, 18, 19]

Q1 = "Pada jam berapa rata-rata penyewaan per jam mencapai puncak pada hari kerja dibandingkan akhir pekan/hari libur sepanjang 2011–2012, dan berapa persen total penyewaan yang terkonsentrasi di jam sibuk (07.00–09.59 dan 16.00–19.59) pada masing-masing tipe hari, sehingga tim operasional dapat menjadwalkan redistribusi dan pemeliharaan sepeda di luar jam tersebut?"
Q2 = "Berapa persen penurunan rata-rata penyewaan harian pada cuaca berkabut dan hujan/salju ringan dibandingkan cuaca cerah pada masing-masing musim sepanjang 2011–2012, serta pengguna mana (casual atau registered) yang paling terdampak, sehingga operator dapat menyiapkan strategi armada dan insentif saat cuaca buruk?"
Q3 = "Berapa pertumbuhan total penyewaan bulanan tahun 2012 dibandingkan 2011 (year-over-year), dan pada bulan apa pertumbuhannya paling rendah, sehingga tim marketing dapat memfokuskan promosi pada bulan tersebut?"


@st.cache_data
def load_data():
    hour = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    day = pd.read_csv(BASE / "day_data.csv", parse_dates=["dteday"])
    day["temp_bin"] = pd.Categorical(day["temp_bin"], ["<10 °C", "10-20 °C", "20-30 °C", ">30 °C"], ordered=True)
    day["demand_level"] = pd.Categorical(day["demand_level"], ["Rendah", "Sedang", "Tinggi"], ordered=True)
    return hour, day


hour_df, day_df = load_data()

# ---------------- Sidebar (filter untuk SELURUH visualisasi) ----------------
with st.sidebar:
    st.title("🚲 Filter")
    min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
    date_range = st.date_input("Rentang tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    seasons = st.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
    all_weather = WEATHER_ORDER + ["Hujan/Salju Lebat"]
    weathers = st.multiselect("Kondisi cuaca", all_weather, default=all_weather)
    st.caption("Semua grafik di dashboard mengikuti filter ini.")
    st.caption("Sumber: Capital Bikeshare, Washington D.C. (2011–2012)")

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:  # pengguna baru memilih satu tanggal
    st.sidebar.info("Pilih tanggal akhir untuk melengkapi rentang.")
    start, end = pd.Timestamp(min_d), pd.Timestamp(max_d)


def apply_filter(df):
    return df[df["dteday"].between(start, end) & df["season_label"].isin(seasons) & df["weather_label"].isin(weathers)]


day_f, hour_f = apply_filter(day_df), apply_filter(hour_df)

st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown("Pola permintaan penyewaan sepeda berdasarkan **jam**, **cuaca/musim**, dan **pertumbuhan bulanan** (2011–2012).")

st.caption(f"Periode ditampilkan: {start:%d %b %Y} – {end:%d %b %Y} | Musim: {', '.join(seasons) or '-'} | "
           f"Cuaca: {', '.join(weathers) or '-'}")

if day_f.empty or hour_f.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan ubah filter.")
    st.stop()

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{day_f['cnt'].sum():,.0f}")
c2.metric("Rata-rata per hari", f"{day_f['cnt'].mean():,.0f}")
c3.metric("Pengguna registered", f"{day_f['registered'].sum() / day_f['cnt'].sum() * 100:.1f}%")
c4.metric("Pengguna casual", f"{day_f['casual'].sum() / day_f['cnt'].sum() * 100:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["⏰ Pertanyaan 1: Jam Sibuk", "🌦️ Pertanyaan 2: Cuaca & Musim",
                                  "📈 Pertanyaan 3: Pertumbuhan Bulanan", "🧩 Analisis Lanjutan"])

# ---------------- Tab 1 ----------------
with tab1:
    st.markdown(f"**Pertanyaan 1:** {Q1}")
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
    ax.set_title("Rata-rata penyewaan per jam: hari kerja vs akhir pekan/libur", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    sns.despine()
    st.pyplot(fig)

    shares = {}
    for t, g in hour_f.groupby("day_type"):
        m = g.groupby("hr")["cnt"].mean()
        shares[t] = m.loc[[h for h in PEAK_HOURS if h in m.index]].sum() / m.sum() * 100
    shares = pd.Series(shares).sort_values()
    fig, ax = plt.subplots(figsize=(8, 3.2))
    bars = ax.barh(shares.index, shares.values,
                   color=[BLUE if i == "Akhir Pekan/Libur" else ORANGE for i in shares.index], height=0.55)
    for b, v in zip(bars, shares.values):
        ax.text(v + 1.2, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center", fontweight="bold")
    ax.set_xlim(0, 80)
    ax.set_xlabel("Porsi penyewaan harian di jam sibuk 07-09 & 16-19 (%)")
    ax.set_ylabel("Tipe hari")
    ax.set_title("Porsi penyewaan di jam sibuk", loc="left", fontweight="bold")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    st.info("Jam sibuk hari kerja sebaiknya dihindari untuk redistribusi/pemeliharaan; gunakan jendela paling sepi "
            "(sekitar 02.00–05.00).")

# ---------------- Tab 2 ----------------
with tab2:
    st.markdown(f"**Pertanyaan 2:** {Q2}")
    avg_w = day_f.groupby("weather_label")["cnt"].mean().reindex(WEATHER_ORDER).dropna()
    base = avg_w.get("Cerah")
    if base is None:
        st.warning("Persentase penurunan dihitung terhadap cuaca cerah. Sertakan 'Cerah' pada filter cuaca.")
    col_a, col_b = st.columns([1, 1.3])
    with col_a:
        fig, ax = plt.subplots(figsize=(5.5, 4.4))
        colors = [ORANGE if w == "Hujan/Salju Ringan" else GREY for w in avg_w.index]
        bars = ax.bar(avg_w.index, avg_w.values, color=colors, width=0.6)
        for b, (w, v) in zip(bars, avg_w.items()):
            label = f"{v:,.0f}"
            if base and w != "Cerah":
                label += f"\n({(v / base - 1) * 100:+.0f}%)"
            ax.text(b.get_x() + b.get_width() / 2, v + avg_w.max() * 0.02, label, ha="center", fontweight="bold", fontsize=9)
        ax.set_ylim(0, avg_w.max() * 1.25)
        ax.set_xlabel("Kondisi cuaca")
        ax.set_ylabel("Rata-rata penyewaan harian (sepeda)")
        ax.set_title("Rata-rata per kondisi cuaca", loc="left", fontweight="bold")
        ax.tick_params(axis="x", labelsize=8)
        sns.despine()
        st.pyplot(fig)
    with col_b:
        pv = day_f.pivot_table(index="season_label", columns="weather_label", values="cnt", aggfunc="mean")
        pv = pv.reindex([s for s in SEASON_ORDER if s in pv.index])
        if "Cerah" in pv.columns:
            drop_s = pd.DataFrame({w: (1 - pv[w] / pv["Cerah"]) * 100
                                   for w in ["Berkabut/Berawan", "Hujan/Salju Ringan"] if w in pv.columns})
            fig, ax = plt.subplots(figsize=(7.5, 4.4))
            drop_s.plot(kind="bar", ax=ax, color=[LIGHT, ORANGE][:drop_s.shape[1]], width=0.75, rot=0)
            for c in ax.containers:
                ax.bar_label(c, fmt="%.0f%%", fontsize=9)
            ax.set_xlabel("Musim")
            ax.set_ylabel("Penurunan dibanding cuaca cerah (%)")
            ax.set_title("Penurunan penyewaan per musim", loc="left", fontweight="bold")
            ax.legend(title="Kondisi cuaca", frameon=False, fontsize=9)
            sns.despine()
            st.pyplot(fig)
        else:
            st.info("Grafik penurunan per musim memerlukan data cuaca 'Cerah' pada filter.")

    users = day_f.groupby("weather_label")[["casual", "registered"]].mean().reindex(WEATHER_ORDER).dropna()
    if "Cerah" in users.index and len(users) > 1:
        ud = ((1 - users / users.loc["Cerah"]) * 100).drop("Cerah")
        fig, ax = plt.subplots(figsize=(7.5, 3.8))
        ud.plot(kind="bar", ax=ax, color=[ORANGE, BLUE], width=0.7, rot=0)
        for c in ax.containers:
            ax.bar_label(c, fmt="%.1f%%", fontsize=9)
        ax.set_xlabel("Kondisi cuaca")
        ax.set_ylabel("Penurunan dibanding cuaca cerah (%)")
        ax.set_title("Pengguna mana yang paling terdampak?", loc="left", fontweight="bold")
        ax.legend(["Casual", "Registered"], frameon=False)
        sns.despine()
        st.pyplot(fig)
    st.caption("Catatan: hari bercuaca hujan/salju ringan jumlahnya sedikit (21 hari pada data penuh), "
               "sehingga angka per musim bersifat indikatif.")

# ---------------- Tab 3 ----------------
with tab3:
    st.markdown(f"**Pertanyaan 3:** {Q3}")
    monthly = day_f.groupby(["mnth", "year"])["cnt"].sum().unstack().reindex(range(1, 13))
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.5, 1]})
    for yr, col in {2011: GREY, 2012: BLUE}.items():
        if yr in monthly.columns and monthly[yr].notna().any():
            ax[0].plot(MONTHS, monthly[yr], marker="o", lw=2.5, color=col, label=str(yr))
    ax[0].set_xlabel("Bulan")
    ax[0].set_ylabel("Total penyewaan per bulan")
    ax[0].set_title("Total penyewaan bulanan", loc="left", fontweight="bold")
    ax[0].yaxis.set_major_formatter(lambda x, p: f"{x / 1000:.0f} rb")
    ax[0].legend(frameon=False)

    both = {2011, 2012} <= set(monthly.columns)
    g = ((monthly[2012] / monthly[2011] - 1) * 100).dropna() if both else pd.Series(dtype=float)
    if not g.empty:
        names = [MONTHS[i - 1] for i in g.index]
        low = g.idxmin()
        ax[1].bar(names, g.values, color=[ORANGE if i == low else GREY for i in g.index])
        ax[1].text(names.index(MONTHS[low - 1]), g[low] + 3, f"Terendah: {MONTHS[low - 1]}\n{g[low]:.0f}%",
                   ha="center", color=ORANGE, fontweight="bold", fontsize=9)
        ax[1].set_ylim(0, max(g.max() * 1.2, 10))
        ax[1].tick_params(axis="x", labelsize=8)
    else:
        ax[1].text(0.5, 0.5, "Pertumbuhan YoY membutuhkan data\n2011 dan 2012 pada bulan yang sama",
                   ha="center", va="center", transform=ax[1].transAxes)
        ax[1].set_xticks([])
        ax[1].set_yticks([])
    ax[1].set_xlabel("Bulan")
    ax[1].set_ylabel("Pertumbuhan (%)")
    ax[1].set_title("Pertumbuhan YoY 2012 vs 2011 (%)", loc="left", fontweight="bold")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    if not g.empty:
        st.info(f"Dalam rentang & filter terpilih, pertumbuhan terendah terjadi pada **{MONTHS[low - 1]}** ({g[low]:.0f}%). "
                "Bulan yang hanya sebagian tercakup oleh rentang tanggal dapat membuat perbandingan kurang akurat.")
    else:
        st.warning("Perluas rentang tanggal agar mencakup bulan yang sama pada 2011 dan 2012.")

# ---------------- Tab 4 ----------------
with tab4:
    st.subheader("Analisis lanjutan: manual grouping & binning")
    c_a, c_b, c_c = st.columns(3)
    seg_order = ["Dini Hari (00-05)", "Sibuk Pagi (06-09)", "Siang (10-15)", "Sibuk Sore (16-19)", "Malam (20-23)"]
    seg = hour_f.pivot_table(index="time_segment", columns="day_type", values="cnt", aggfunc="mean").reindex(seg_order)
    with c_a:
        st.markdown("**Segmen waktu**")
        fig, ax = plt.subplots(figsize=(5, 4.4))
        seg.plot(kind="bar", ax=ax, color=[ORANGE if c == "Hari Kerja" else BLUE for c in seg.columns], rot=35, width=0.75)
        ax.set_xlabel("Segmen waktu")
        ax.set_ylabel("Rata-rata sepeda per jam")
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
        ax.set_xlabel("Rentang suhu")
        ax.set_ylabel("Rata-rata penyewaan harian")
        sns.despine()
        st.pyplot(fig)
    with c_c:
        st.markdown("**Tingkat permintaan per musim**")
        dem = pd.crosstab(day_f["season_label"], day_f["demand_level"], normalize="index") * 100
        dem = dem.reindex([s for s in SEASON_ORDER if s in dem.index])
        fig, ax = plt.subplots(figsize=(5, 4.4))
        dem.plot(kind="bar", stacked=True, ax=ax, color=[GREY, LIGHT, BLUE][:dem.shape[1]], rot=0, width=0.7)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Persentase hari (%)")
        ax.legend(title="", frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
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

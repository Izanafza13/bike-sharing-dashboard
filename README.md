# Proyek Analisis Data: Bike Sharing Dataset 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011–2012) beserta dashboard interaktif Streamlit.

**Demo dashboard:** https://bike-sharing-dashboard-analytics.streamlit.app/

## Pertanyaan Bisnis
1. Pada jam berapa permintaan memuncak pada hari kerja vs akhir pekan/libur, dan berapa persen permintaan terkonsentrasi di jam sibuk?
2. Berapa persen penurunan penyewaan akibat cuaca berkabut dan hujan/salju ringan di tiap musim, dan pengguna mana yang paling terdampak?
3. Berapa pertumbuhan penyewaan bulanan 2012 vs 2011 dan bulan mana yang paling rendah pertumbuhannya?

## Temuan Utama
- **Jam sibuk:** hari kerja memuncak sekitar pukul 08.00 dan 17.00. Tujuh jam sibuk (07.00–09.59 dan 16.00–19.59) menyumbang ≈57,9% penyewaan hari kerja, dibanding ≈34,8% pada akhir pekan/libur.
- **Cuaca:** dibanding cuaca cerah, cuaca berkabut menurunkan penyewaan ≈17,2% dan hujan/salju ringan ≈63,0%. Pengguna *casual* turun ≈80,8%, *registered* ≈58,7%. Hanya ada 21 hari hujan/salju ringan pada data harian, sehingga angka per musim bersifat indikatif.
- **Pertumbuhan:** total penyewaan 2012 tumbuh ≈64,9% dibanding 2011 dan positif di semua bulan. Pertumbuhan terendah terjadi pada Juni (≈41%).

## Struktur Direktori
```
bike-sharing-dashboard
├── dashboard
│   ├── dashboard.py
│   ├── main_data.csv     # data per jam yang sudah dibersihkan
│   └── day_data.csv      # data harian yang sudah dibersihkan
├── data
│   ├── day.csv
│   ├── hour.csv
│   └── Readme.txt
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

Gunakan Python 3.11 atau lebih baru.

### Clone repository
```
git clone https://github.com/Izanafza13/bike-sharing-dashboard.git
cd bike-sharing-dashboard
```

### Menggunakan virtual environment (venv)
```
python -m venv venv
source venv/bin/activate        # Windows (PowerShell): venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Menggunakan Anaconda
```
conda create --name bike-ds python=3.11
conda activate bike-ds
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `bike-sharing-dashboard`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Buka `notebook.ipynb` dengan Jupyter/Colab dari folder `bike-sharing-dashboard` (agar path `data/` dan `dashboard/` terbaca). Menjalankan seluruh sel akan menghasilkan ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`. Untuk menjalankan notebook secara lokal, tambahkan `jupyter` ke environment Anda (`pip install jupyter`).

## Teknik Analisis Lanjutan
Manual grouping (segmen waktu, tingkat permintaan harian) dan binning (rentang suhu). RFM dan geospasial tidak digunakan karena dataset tidak memuat data pelanggan individu maupun lokasi.

## Sumber Data
Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", Progress in Artificial Intelligence (2013), doi:10.1007/s13748-013-0040-3.

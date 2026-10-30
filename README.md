# Proyek Analisis Data: Bike Sharing Dataset 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011–2012) beserta dashboard interaktif Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa permintaan memuncak pada hari kerja vs akhir pekan/libur, dan berapa persen permintaan terkonsentrasi di jam sibuk?
2. Berapa persen penurunan penyewaan akibat cuaca berkabut dan hujan/salju ringan di tiap musim, dan pengguna mana yang paling terdampak?
3. Berapa pertumbuhan penyewaan bulanan 2012 vs 2011 dan bulan mana yang paling rendah pertumbuhannya?

## Struktur Direktori
```
submission
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

### Menggunakan virtual environment (venv)
```
python -m venv venv
source venv/bin/activate        # Powershell : venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Menggunakan Anaconda
```
conda create --name bike-ds python=3.11
conda activate bike-ds
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Buka `notebook.ipynb` dengan Jupyter/Colab dari folder `submission` (agar path `data/` dan `dashboard/` terbaca). Menjalankan seluruh sel akan menghasilkan ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`. Untuk menjalankan notebook secara lokal, tambahkan `jupyter` ke environment Anda (`pip install jupyter`).

## Teknik Analisis Lanjutan
Manual grouping (segmen waktu, tingkat permintaan harian) dan binning (rentang suhu). RFM dan geospasial tidak digunakan karena dataset tidak memuat data pelanggan individu maupun lokasi.

## Sumber Data
Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", Progress in Artificial Intelligence (2013), doi:10.1007/s13748-013-0040-3.

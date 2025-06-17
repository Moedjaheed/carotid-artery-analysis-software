# 🆕 FRAME COMPARISON VIEWER - Quick Start Guide

## Fitur Baru: Frame Comparison Viewer

**Frame Comparison Viewer** adalah menu baru yang memungkinkan Anda untuk:
- Membandingkan dua frame secara bersamaan (side-by-side)
- Menggunakan 2 garis vertikal pada grafik untuk menunjukkan posisi frame
- Melihat detail Diameter dan Pressure untuk setiap frame
- Interaksi langsung dengan grafik (click untuk memilih frame)

## 🚀 Cara Menjalankan

### Method 1: Via Launcher (MUDAH)
```batch
# 1. Jalankan launcher utama
run_launcher.bat

# 2. Pilih opsi 'F' untuk Frame Comparison Viewer
Your choice (D/F/G/Enter): F
```

### Method 2: Direct Launch
```batch
python frame_comparison_viewer.py
```

## 🎯 Cara Menggunakan

### 1. Load Subject
1. Pilih subject dari dropdown menu
2. Klik "Load Selected" untuk memuat data
3. Tunggu sampai video dan data termuat

### 2. Pilih Frame untuk Perbandingan
**Opsi A - Menggunakan Slider:**
- **Frame 1 (Biru)**: Gunakan slider "Frame 1" 
- **Frame 2 (Merah)**: Gunakan slider "Frame 2"

**Opsi B - Click pada Grafik (INTERAKTIF):**
- **Left Click**: Set Frame 1 (garis biru)
- **Right Click**: Set Frame 2 (garis merah)

### 3. Analisis Hasil
- **Frame Display**: Kedua frame ditampilkan side-by-side
- **Data Display**: Diameter dan Pressure ditampilkan untuk setiap frame
- **Grafik**: Garis vertikal biru dan merah menunjukkan posisi frame

## 📊 Contoh Tampilan

```
Frame 1: 150/500 | Diameter: 45.23 | Pressure: 120.5 (BIRU)
Frame 2: 300/500 | Diameter: 42.18 | Pressure: 115.2 (MERAH)

┌─────────────────┐  ┌─────────────────────────────┐
│ Frame 1         │  │     Grafik dengan           │
│ [Gambar]        │  │     Garis Vertikal          │
├─────────────────┤  │                             │
│ Frame 2         │  │  ─●─ Frame 1 (Biru)         │
│ [Gambar]        │  │      ─●─ Frame 2 (Merah)    │
└─────────────────┘  └─────────────────────────────┘
```

## 🔧 Fitur Unggulan

### ✨ Interactive Plot
- **Click pada grafik** untuk langsung memilih frame
- **Real-time update** saat menggeser slider
- **Color-coded** indicators (biru/merah)

### 📈 Dual Data Display
- **Diameter values** untuk kedua frame
- **Pressure values** untuk kedua frame  
- **Frame counter** (contoh: 150/500)

### 🎨 Theme Support
- **Light Theme**: Theme terang
- **Dark Theme**: Theme gelap
- **Menu**: Theme → Light/Dark Theme

## 🆘 Troubleshooting

### Error: "No subjects found"
**Solution**: Pastikan folder `data_uji/` berisi folder subject dengan file .mp4

### Error: "No diameter data found"
**Solution**: Jalankan inference terlebih dahulu untuk generate diameter data

### Error: Loading failed
**Solutions**:
1. Install dependencies: `pip install -r requirements.txt`
2. Check environment: `conda activate ridho-ta`
3. Verify files exist di folder project

## 🔗 Menu Launcher yang Diperbarui

Launcher (`run_launcher.bat`) sekarang memiliki:

```
Quick Launch Options:
[D] Launch Enhanced Data Viewer directly
[F] Launch Frame Comparison Viewer (NEW!) 👈
[G] Launch Full GUI Launcher
```

## 💡 Tips Penggunaan

1. **Pilih Frame Strategis**: Pilih frame pada puncak dan lembah untuk analisis optimal
2. **Gunakan Click Interaction**: Lebih cepat dari slider untuk selection frame
3. **Perhatikan Color Coding**: Biru untuk Frame 1, Merah untuk Frame 2
4. **Switch Theme**: Gunakan dark theme untuk kenyamanan mata

## 📋 Requirements

**Minimal Requirements:**
- Python 3.8+
- Conda environment: `ridho-ta`
- Dependencies: opencv-python, pandas, matplotlib, tkinter, pillow

**Data Requirements:**
- Video files: `data_uji/SubjekN/SubjekN.mp4`
- Diameter data: `inference_results/SubjekN/diameter_data*.csv`
- Pressure data: `data_uji/SubjekN/subjectN.csv` (optional)

---

## 🎉 SIAP DIGUNAKAN!

**Frame Comparison Viewer sudah siap digunakan!** 

Cukup jalankan `run_launcher.bat` dan tekan **'F'** untuk mengakses fitur baru ini.

*Happy analyzing! 🔬📊*

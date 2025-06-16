# Enhanced Inference dengan Multiple Subject Selection dan Model Selection

## 🎯 Fitur Baru

### Multiple Subject Selection (Checkbox)
- **Pilih Multiple Subjects**: Gunakan checkbox untuk memilih subjects mana saja yang ingin di-inference
- **Select All/Deselect All**: Tombol untuk memilih atau membatalkan semua subjects sekaligus
- **Status Indicators**: 
  - 🎥 = Video file tersedia
  - 📊 = Pressure data tersedia  
  - ⏰ = Timestamp data tersedia
  - ❌ = File tidak tersedia

### Model Selection (Radiobutton)
- **Pilih Model AI**: Radiobutton untuk memilih model UNet yang ingin digunakan
- **Auto-detect Models**: Sistem otomatis mendeteksi file .pth di direktori
- **Custom Model**: Option untuk browse dan pilih model custom
- **Model Info**: Menampilkan ukuran file dan tanggal modifikasi model

### Enhanced Processing Options
- **Pressure Integration**: Toggle untuk mengaktifkan enhanced processing dengan pressure data
- **Output Settings**: 
  - Individual subject results
  - Combined analysis report
- **Configuration Save/Load**: Simpan dan load konfigurasi processing

## 🚀 Cara Penggunaan

### 1. Akses Enhanced Inference
- Jalankan `run_launcher.bat`
- Pilih **Enhanced Inference (Multiple Subjects + Model Selection)**
- Atau tekan tombol **Enhanced Inference** di tab Inference

### 2. Subject Selection Tab
1. **Auto-scan Subjects**: Sistem otomatis scan folder `data_uji/`
2. **Pilih Subjects**: Centang checkbox subjects yang ingin diproses
3. **Check Status**: Lihat status indicator untuk memastikan file tersedia
4. **Select All/Deselect All**: Gunakan tombol untuk memilih semua atau tidak sama sekali

### 3. Model Selection Tab  
1. **Auto-scan Models**: Sistem scan file .pth di direktori saat ini
2. **Pilih Model**: Pilih radiobutton model yang ingin digunakan
3. **Custom Model**: Browse untuk pilih model dari lokasi lain
4. **Refresh Models**: Update list model jika ada yang baru

### 4. Processing Options Tab
1. **Enhanced Processing**: 
   - ✅ Aktifkan untuk integrasi pressure data
   - Memerlukan file `subjectN.csv` dan `timestamps.csv`
2. **Output Settings**:
   - Individual results: Hasil per subject terpisah
   - Combined report: Laporan gabungan semua subjects

### 5. Progress Tab
1. **Status Monitor**: Lihat status processing real-time
2. **Progress Bar**: Visual progress indicator
3. **Processing Log**: Detail log setiap step processing

### 6. Start Processing
1. **Validasi**: Sistem check subjects dan model yang dipilih
2. **Start Processing**: Klik tombol hijau untuk mulai
3. **Monitor Progress**: Lihat progress di Progress tab
4. **Stop Processing**: Tombol merah untuk stop jika diperlukan

## 📁 Struktur Input yang Diperlukan

### Untuk Standard Processing:
```
data_uji/
├── Subjek1/
│   ├── Subjek1.mp4          # Video file (WAJIB)
│   └── pictures/            # Optional
├── Subjek2/
│   ├── Subjek2.mp4
│   └── pictures/
```

### Untuk Enhanced Processing:
```
data_uji/
├── Subjek1/
│   ├── Subjek1.mp4          # Video file (WAJIB)
│   ├── subject1.csv         # Pressure data (untuk enhanced)
│   ├── timestamps.csv       # Timestamp data (untuk enhanced)
│   └── pictures/
├── Subjek2/
│   ├── Subjek2.mp4
│   ├── subject2.csv
│   ├── timestamps.csv
│   └── pictures/
```

## 📊 Output yang Dihasilkan

### Individual Subject Output:
```
inference_results/
├── Subjek1/
│   ├── Subjek1_segmented_video.mp4         # Video dengan overlay
│   ├── Subjek1_diameter_plot.png           # Plot diameter vs frame
│   ├── Subjek1_diameter_data.csv           # Data diameter per frame
│   ├── Subjek1_diameter_data_with_pressure.csv  # Enhanced data
│   ├── Subjek1_diameter_plot_with_pressure.png  # Enhanced plot
│   └── Subjek1_correlation_analysis.png    # Analisis korelasi
├── Subjek2/
│   └── ...
```

### Combined Report (jika diaktifkan):
- Statistical summary semua subjects
- Comparative analysis
- Combined visualizations

## ⚙️ Configuration Management

### Save Configuration
1. Set pilihan subjects dan model
2. Klik **Save Configuration**
3. Pilih lokasi file .json
4. Konfigurasi tersimpan untuk penggunaan berikutnya

### Load Configuration  
1. Klik **Load Configuration**
2. Pilih file .json konfigurasi
3. Semua setting otomatis ter-load
4. Review dan modify jika perlu

## 🔧 Troubleshooting

### Subject tidak terdeteksi
- Pastikan folder `data_uji/` ada
- Pastikan nama folder subject sesuai dengan nama file video
- Klik **Refresh** untuk scan ulang

### Model tidak terdeteksi
- Pastikan file .pth ada di direktori yang sama
- File model harus berekstensi .pth
- Klik **Refresh Models** untuk scan ulang

### Enhanced processing gagal
- Pastikan file `subject1.csv`, `timestamps.csv` ada
- Check format data CSV sesuai spesifikasi
- Lihat log error untuk detail masalah

### Processing timeout
- Default timeout 1 jam per subject
- Untuk video besar, processing bisa lama
- Monitor progress di log

## 📋 Tips Penggunaan

1. **Batch Processing**: Pilih multiple subjects untuk efficiency
2. **Model Comparison**: Jalankan dengan model berbeda untuk compare hasil
3. **Configuration**: Save konfigurasi untuk penggunaan berulang
4. **Monitoring**: Always monitor progress log untuk detect issues
5. **Storage**: Pastikan disk space cukup untuk output files

## 🆕 Keunggulan vs Versi Lama

| Fitur | Versi Lama | Versi Baru |
|-------|------------|------------|
| Subject Selection | Single, manual | Multiple checkbox |
| Model Selection | Fixed | Radiobutton selection |
| Progress Monitoring | None | Real-time log + progress bar |
| Configuration | None | Save/Load JSON |
| Batch Processing | Manual loop | Integrated batch |
| Error Handling | Basic | Comprehensive |
| User Interface | Command line | Full GUI |

## 🔗 File Terkait

- `enhanced_inference_gui.py` - GUI utama
- `video_inference.py` - Processing engine
- `launcher_with_inference_log.py` - Launcher integration
- `run_launcher.bat` - Batch launcher

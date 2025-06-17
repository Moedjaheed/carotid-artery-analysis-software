# Frame Comparison Viewer - Dokumentasi

## Deskripsi
Frame Comparison Viewer adalah fitur baru yang memungkinkan analisis perbandingan frame-by-frame dengan indikator garis vertikal ganda pada grafik diameter vs pressure. Tool ini dirancang untuk memberikan analisis visual yang lebih mendalam terhadap perubahan diameter arteri pada frame tertentu.

## Fitur Utama

### 1. Dual Frame Display
- **Frame 1 (Blue Line)**: Frame pertama yang dipilih untuk perbandingan
- **Frame 2 (Red Line)**: Frame kedua yang dipilih untuk perbandingan
- **Side-by-side Display**: Kedua frame ditampilkan secara bersamaan untuk perbandingan visual langsung

### 2. Interactive Vertical Line Indicators
- **Blue Vertical Line**: Menunjukkan posisi Frame 1 pada grafik
- **Red Vertical Line**: Menunjukkan posisi Frame 2 pada grafik
- **Real-time Update**: Garis vertikal bergerak sesuai dengan perubahan frame yang dipilih

### 3. Interactive Plot Selection
- **Left Click**: Mengatur posisi Frame 1
- **Right Click**: Mengatur posisi Frame 2
- **Instant Update**: Frame langsung berubah saat mengklik pada grafik

### 4. Real-time Data Display
- **Diameter Information**: Nilai diameter untuk setiap frame yang dipilih
- **Pressure Information**: Nilai pressure untuk setiap frame yang dipilih
- **Color-coded Display**: Informasi ditampilkan dengan warna yang sesuai (biru untuk Frame 1, merah untuk Frame 2)

### 5. Advanced Slider Controls
- **Dual Sliders**: Slider terpisah untuk Frame 1 dan Frame 2
- **Frame Counter**: Menampilkan nomor frame saat ini dari total frame
- **Smooth Navigation**: Navigasi frame yang halus dan responsif

## Cara Penggunaan

### 1. Menjalankan Frame Comparison Viewer

#### Melalui Launcher Utama:
```batch
# Jalankan run_launcher.bat
run_launcher.bat

# Pilih opsi F untuk Frame Comparison Viewer
Your choice (D/F/G/Enter): F
```

#### Atau langsung:
```batch
python frame_comparison_viewer.py
```

### 2. Loading Data
1. **Subject Selection**: Pilih subject dari dropdown menu
2. **Load Selected**: Klik tombol "Load Selected" untuk memuat data
3. **Alternative**: Gunakan "Browse..." untuk memilih folder custom

### 3. Frame Comparison
1. **Set Frame 1**: Gunakan slider "Frame 1" (biru) untuk memilih frame pertama
2. **Set Frame 2**: Gunakan slider "Frame 2" (merah) untuk memilih frame kedua
3. **View Comparison**: Kedua frame akan ditampilkan secara bersamaan

### 4. Interactive Plot Navigation
1. **Left Click on Plot**: Mengatur Frame 1 ke posisi yang diklik
2. **Right Click on Plot**: Mengatur Frame 2 ke posisi yang diklik
3. **Visual Feedback**: Garis vertikal akan bergerak sesuai dengan pilihan

## Struktur Data yang Didukung

### 1. Video Files
- **Format**: MP4
- **Location**: `data_uji/SubjekN/SubjekN.mp4`
- **Segmented Video**: `inference_results/SubjekN/*segmented_video*.mp4` (prioritas utama)

### 2. Diameter Data
- **Format**: CSV
- **Location**: `inference_results/SubjekN/*diameter_data*.csv`
- **Required Columns**: `frame`, `diameter`

### 3. Pressure Data
- **Format**: CSV
- **Location**: `data_uji/SubjekN/subjectN.csv`
- **Required Columns**: `pressure` atau `Pressure`

## Fitur Tambahan

### 1. Theme Support
- **Light Theme**: Theme terang untuk penggunaan normal
- **Dark Theme**: Theme gelap untuk penggunaan dalam kondisi cahaya rendah
- **Menu Access**: Theme → Light/Dark Theme

### 2. Help System
- **About Dialog**: Informasi tentang aplikasi
- **Usage Instructions**: Panduan penggunaan lengkap
- **Menu Access**: Help → About / Usage Instructions

### 3. Data Synchronization
- **Automatic Sync**: Data diameter dan pressure disinkronisasi otomatis
- **Frame-based Indexing**: Semua data diindeks berdasarkan nomor frame
- **Smart Merging**: Penggabungan data yang cerdas berdasarkan struktur yang tersedia

## Output dan Display

### 1. Frame Information Display
```
Frame 1: 150/500 | Diameter: 45.23 | Pressure: 120.5
Frame 2: 300/500 | Diameter: 42.18 | Pressure: 115.2
```

### 2. Plot Features
- **Dual Y-axis**: Diameter (kiri) dan Pressure (kanan)
- **Grid Lines**: Grid untuk memudahkan pembacaan
- **Legend**: Keterangan untuk setiap line dan indikator
- **Color Coding**: Biru untuk diameter, hijau untuk pressure, garis vertikal sesuai frame

### 3. Status Information
```
Loaded Subjek1 - 500 frames | Data: Diameter ✅, Pressure ✅
```

## Troubleshooting

### 1. Error Loading Video
```
ERROR: No video files found in selected folder
```
**Solution**: Pastikan folder subject mengandung file .mp4

### 2. Error Loading Data
```
DEBUG: No diameter data found
```
**Solution**: Pastikan inference sudah dijalankan dan menghasilkan file diameter_data.csv

### 3. Display Issues
```
ERROR: Frame Comparison Viewer failed to start
```
**Solutions**:
- Install dependencies: `pip install -r requirements.txt`
- Check tkinter availability
- Verify matplotlib and PIL installation

### 4. Theme Issues
```
Theme application error: [error message]
```
**Solution**: Reset theme ke default melalui Theme → Reset to Default

## Dependencies

### Required Packages
```python
opencv-python
pandas
numpy
tkinter (biasanya included dengan Python)
matplotlib
pillow (PIL)
glob
```

### Installation Command
```batch
pip install opencv-python pandas numpy matplotlib pillow
```

## File Structure yang Diharapkan

```
project_root/
├── frame_comparison_viewer.py
├── theme_manager.py
├── data_uji/
│   ├── Subjek1/
│   │   ├── Subjek1.mp4
│   │   └── subject1.csv (pressure data)
│   └── Subjek2/
│       ├── Subjek2.mp4
│       └── subject2.csv
├── inference_results/
│   ├── Subjek1/
│   │   ├── diameter_data_with_pressure.csv
│   │   └── segmented_video.mp4
│   └── Subjek2/
│       └── diameter_data.csv
└── run_launcher.bat
```

## Keunggulan Frame Comparison Viewer

### 1. Visual Comparison
- **Side-by-side Display**: Perbandingan visual langsung antara dua frame
- **Real-time Updates**: Perubahan frame langsung terlihat
- **High-quality Display**: Resolusi optimal untuk analisis detail

### 2. Interactive Analysis
- **Click-to-Select**: Pemilihan frame melalui click pada grafik
- **Dual Slider Control**: Kontrol independen untuk setiap frame
- **Instant Feedback**: Response langsung terhadap perubahan

### 3. Data Integration
- **Comprehensive Data**: Menampilkan diameter dan pressure secara bersamaan
- **Smart Synchronization**: Sinkronisasi data otomatis
- **Color-coded Information**: Informasi dengan kode warna untuk kemudahan

### 4. Advanced Visualization
- **Dual Vertical Lines**: Indikator posisi frame pada grafik
- **Interactive Plot**: Plot yang responsif terhadap input user
- **Professional Layout**: Tata letak yang intuitif dan profesional

## Use Cases

### 1. Clinical Analysis
- **Peak Detection**: Identifikasi perbedaan diameter pada puncak dan lembah
- **Cycle Comparison**: Perbandingan berbagai titik dalam siklus jantung
- **Anomaly Detection**: Deteksi anomali dengan membandingkan frame normal dan abnormal

### 2. Research Applications
- **Data Validation**: Validasi hasil pengukuran pada titik tertentu
- **Trend Analysis**: Analisis tren perubahan diameter
- **Quality Control**: Kontrol kualitas hasil segmentasi

### 3. Educational Purposes
- **Teaching Tool**: Alat bantu pengajaran untuk memahami dinamika arteri
- **Demonstration**: Demonstrasi perubahan diameter dalam siklus jantung
- **Interactive Learning**: Pembelajaran interaktif dengan visual feedback

## Integrasi dengan Sistem Utama

Frame Comparison Viewer terintegrasi penuh dengan sistem utama melalui:

1. **Launcher Integration**: Akses langsung melalui run_launcher.bat dengan opsi 'F'
2. **Data Compatibility**: Menggunakan struktur data yang sama dengan Enhanced Data Viewer
3. **Theme Consistency**: Menggunakan theme_manager yang sama
4. **Error Handling**: Sistem error handling yang konsisten

## Update dan Pengembangan

### Version 1.0 Features
- ✅ Dual frame display
- ✅ Interactive vertical line indicators
- ✅ Plot click selection
- ✅ Real-time data display
- ✅ Theme support
- ✅ Help system

### Rencana Pengembangan
- [ ] Frame difference visualization
- [ ] Multiple frame comparison (3+ frames)
- [ ] Export comparison results
- [ ] Measurement tools
- [ ] Animation between frames

---

**Catatan**: Frame Comparison Viewer adalah fitur experimental yang terus dikembangkan. Laporkan bug atau saran pengembangan untuk perbaikan lebih lanjut.

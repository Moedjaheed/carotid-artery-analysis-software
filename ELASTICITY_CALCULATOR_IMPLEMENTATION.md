# Elasticity Calculator - New Feature Implementation

## Overview
Elasticity Calculator adalah menu/tool baru yang telah diimplementasikan untuk menghitung parameter elastisitas arteri karotis. Tool ini mirip dengan Frame Comparison Viewer tetapi dengan tambahan kolom untuk perhitungan elastisitas berdasarkan empat persamaan utama.

## Features Implemented

### 1. User Interface
- **Subject Selection**: Dropdown untuk memilih subjek yang tersedia
- **Frame Selection**: Dua spinbox untuk memilih baseline frame dan compressed frame
- **Probe Configuration**: Input untuk area kontak probe (default: 1.0 cm²)
- **Video Display**: Menampilkan frame video dengan kontrol navigasi
- **Data Visualization**: Plot untuk diameter dan pressure vs frame number

### 2. Data Display
- **Frame Data Table**: Menampilkan data diameter dan pressure untuk baseline dan compressed frame
- **Difference Calculation**: Menghitung selisih diameter dan pressure antara kedua frame
- **Real-time Updates**: Data diperbarui secara otomatis saat frame selection berubah

### 3. Elasticity Calculations
Tool ini menghitung keempat parameter elastisitas sesuai persamaan yang diminta:

#### A. Strain (ε)
- **Formula**: ε = (D_compressed - D_baseline) / D_baseline  
- **Unit**: Unitless
- **Description**: Perubahan relatif diameter arteri akibat tekanan

#### B. Peterson Elastic Modulus (PEM)
- **Formula**: PEM = ΔP / ε = (ΔP × D_baseline) / (D_compressed - D_baseline)
- **Unit**: mmHg
- **Description**: Mengukur kekakuan dinding arteri terhadap tekanan luar

#### C. Stiffness Parameter (β)
- **Formula**: β = ln(P_compressed / P_baseline) / ε
- **Unit**: Unitless  
- **Description**: Parameter tak berdimensi untuk perbandingan kekakuan arteri

#### D. Distensibility (DC)
- **Formula**: DC = 2(D_compressed - D_baseline) / (D_baseline × ΔP)
- **Unit**: × 10⁻⁵ Pa⁻¹
- **Description**: Kemampuan dinding arteri untuk mengembang akibat tekanan

### 4. Clinical Interpretation
Setiap parameter elastisitas disertai dengan interpretasi klinis berdasarkan literatur:

- **PEM**: Normal (<495 mmHg), Borderline (495-630 mmHg), Elevated (>630 mmHg)
- **Stiffness β**: Normal (<13.0), Atherosclerosis risk (≥13.0), High CAD risk (≥20.0)
- **Distensibility**: Normal (>4.0), Reduced (3.0-4.0), Significantly reduced (<3.0)

### 5. Export and Help
- **Export Function**: Menyimpan hasil perhitungan ke file CSV
- **Help Dialog**: Menampilkan formula, deskripsi, dan referensi literatur

## Integration with Main Launcher

### 1. Menu Integration
Elasticity Calculator telah diintegrasikan ke dalam launcher utama (`launcher_enhanced_fixed.py`):
- **Location**: Tab "🔧 Tools" → Section "Analysis Tools"  
- **Button**: "📊 Elasticity Calculator"
- **Companion**: "📈 Frame Comparison" (untuk Frame Comparison Viewer)

### 2. Launch Methods
Dua method baru ditambahkan ke launcher:
- `launch_elasticity_calculator()`: Menjalankan Elasticity Calculator
- `launch_frame_comparison()`: Menjalankan Frame Comparison Viewer

## Technical Implementation

### 1. File Structure
```
elasticity_calculator.py - Main application file
launcher_enhanced_fixed.py - Updated with new menu buttons
theme_manager.py - Theme support (fixed compatibility)
```

### 2. Data Compatibility
- Menggunakan data yang sama dengan Frame Comparison Viewer
- Memuat data dari `inference_results/{subject}/{subject}_diameter_data.csv`
- Support untuk data dengan kolom pressure terintegrasi
- Automatic data syncing dan validation

### 3. Error Handling
- Robust error handling untuk file loading
- Data validation untuk perhitungan elastisitas
- User-friendly error messages
- Debug logging untuk troubleshooting

## Usage Instructions

### 1. From Main Launcher
1. Jalankan `launcher_enhanced_fixed.py`
2. Buka tab "🔧 Tools"
3. Click "📊 Elasticity Calculator"

### 2. Direct Launch
```bash
python elasticity_calculator.py
```

### 3. Using the Tool
1. **Select Subject**: Pilih subjek dari dropdown
2. **Set Probe Area**: Masukkan area kontak probe (default: 1.0 cm²)
3. **Select Frames**: 
   - Baseline Frame: Frame saat kondisi normal/relaksasi
   - Compressed Frame: Frame saat arteri terkompresi maksimal
4. **Calculate**: Click "Calculate Elasticity Parameters"
5. **Review Results**: Lihat nilai dan interpretasi klinis
6. **Export**: Simpan hasil jika diperlukan

## References
Tool ini menggunakan nilai referensi dari literatur medis:
- MESA Study (Pewowaruk et al.) - untuk nilai PEM
- Morioka et al. - untuk nilai Stiffness β
- Cantón et al. - untuk nilai Distensibility

## Testing Status
✅ **Completed**: 
- UI implementation dan integration
- All four elasticity calculations working
- Clinical interpretation system
- Data loading dan synchronization
- Export functionality
- Theme support compatibility
- Main launcher integration

✅ **Tested**:
- Elasticity Calculator runs independently
- Integration with main launcher functional
- Data loading from existing subjects
- Theme manager compatibility fixed

## Future Enhancements
- Batch processing untuk multiple subjects
- Advanced statistical analysis
- Graphical comparison between subjects
- Report generation dengan clinical recommendations

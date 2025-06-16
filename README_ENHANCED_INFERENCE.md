# 🎯 Enhanced Inference - Multiple Subject & Model Selection

## Fitur Baru yang Ditambahkan

### ✅ Multiple Subject Selection dengan Checkbox
- Pilih beberapa subjects sekaligus untuk batch processing
- Checkbox interface yang user-friendly
- Status indicator untuk setiap subject (video, pressure, timestamp)
- Select All / Deselect All buttons
- Auto-refresh untuk detect subjects baru

### ✅ Model Selection dengan Radiobutton  
- Pilih model AI yang ingin digunakan
- Auto-detect semua file .pth di direktori
- Custom model browser untuk model di lokasi lain
- Model info: ukuran file dan tanggal modifikasi

### ✅ Enhanced Processing Options
- Toggle enhanced processing dengan pressure integration
- Output settings (individual/combined reports)
- Configuration save/load functionality

### ✅ Progress Monitoring
- Real-time progress bar
- Detailed processing log
- Status monitoring untuk setiap subject
- Stop/resume functionality

## Cara Menggunakan

### 1. Melalui Run Launcher
```bash
# Jalankan launcher utama
run_launcher.bat

# Pilih: Enhanced Inference (Multiple Subjects + Model Selection)
```

### 2. Melalui GUI Launcher
```bash
# Jalankan GUI launcher
python launcher_with_inference_log.py

# Klik tombol "Enhanced Inference (Multiple Subjects + Model Selection)"
```

### 3. Direct Launch
```bash
# Langsung jalankan Enhanced Inference GUI
python enhanced_inference_gui.py
```

### 4. Test Mode
```bash
# Test implementasi
python test_enhanced_inference.py
```

## Struktur File yang Diperlukan

### Standard Processing
```
data_uji/
├── Subjek1/
│   └── Subjek1.mp4
├── Subjek2/
│   └── Subjek2.mp4
```

### Enhanced Processing (dengan pressure data)
```
data_uji/
├── Subjek1/
│   ├── Subjek1.mp4
│   ├── subject1.csv         # Pressure data
│   └── timestamps.csv       # Timestamp synchronization
├── Subjek2/
│   ├── Subjek2.mp4
│   ├── subject2.csv
│   └── timestamps.csv
```

### Models
```
# Model files di root directory
UNet_25Mei_Sore.pth
UNet_13Mei_dini.pth
UNet_22Mei_Sore.pth
# atau model custom di lokasi lain
```

## Output yang Dihasilkan

### Per Subject
```
inference_results/
├── Subjek1/
│   ├── Subjek1_segmented_video.mp4
│   ├── Subjek1_diameter_plot.png
│   ├── Subjek1_diameter_data.csv
│   └── [enhanced files jika pressure tersedia]
├── Subjek2/
│   └── ...
```

## Keunggulan Baru

| Aspect | Before | After |
|--------|--------|-------|
| Subject Selection | Manual, one-by-one | Multiple checkbox selection |
| Model Selection | Fixed single model | Radiobutton model choice |
| Progress Monitoring | None | Real-time progress + log |
| Batch Processing | Manual repetition | Integrated batch processing |
| Configuration | None | Save/Load settings |
| User Interface | Command line | Full GUI with tabs |
| Error Handling | Basic | Comprehensive with logging |

## Tips Penggunaan

1. **Batch Efficiency**: Pilih multiple subjects untuk processing yang efisien
2. **Model Comparison**: Coba model berbeda untuk compare hasil
3. **Save Configuration**: Simpan setting untuk penggunaan berulang
4. **Monitor Progress**: Selalu check progress log untuk error detection
5. **Enhanced Processing**: Gunakan jika pressure data tersedia untuk analysis yang lebih komprehensif

## Troubleshooting

### GUI tidak muncul
- Pastikan tkinter installed: `pip install tkinter`
- Check Python version compatibility

### Subject tidak terdeteksi
- Pastikan folder `data_uji/` exists
- Check nama folder sesuai dengan nama video file
- Klik Refresh untuk rescan

### Model tidak terdeteksi
- Pastikan file .pth ada di direktori
- Check file permissions
- Klik Refresh Models

### Processing gagal
- Check log untuk error details
- Pastikan dependencies installed: `pip install -r requirements.txt`
- Verify input file formats

## File Dependencies

- `enhanced_inference_gui.py` - Main GUI interface
- `video_inference.py` - Processing engine
- `launcher_with_inference_log.py` - Integrated launcher
- `requirements.txt` - Python dependencies
- Model files (.pth) - AI models

## Next Steps

1. Test dengan real data
2. Customize model selection list
3. Add more processing options
4. Implement result comparison tools
5. Add export functionality untuk hasil batch processing

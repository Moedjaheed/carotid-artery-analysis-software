"""
Data Synchronization Script
Script untuk menyinkronkan data tekanan dan diameter berdasarkan timestamps
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.interpolate import interp1d

def sync_pressure_with_image_data(subject_number):
    """
    Sinkronkan data tekanan dan diameter berdasarkan timestamps.
    
    Args:
        subject_number (int): Nomor subjek (1-7)
    
    Returns:
        pandas.DataFrame: DataFrame yang berisi data yang telah disinkronkan
    """
    try:
        # Baca file timestamps.csv dan subject{X}.csv
        base_path = rf"D:\Ridho\TA\fix banget\Dataset\Subjek{subject_number}"
        timestamp_path = os.path.join(base_path, "timestamps.csv")
        pressure_path = os.path.join(base_path, f"subject{subject_number}.csv")
        diameter_path = f"subjek{subject_number}_diameter_data.csv"
        
        # Baca data
        timestamps_df = pd.read_csv(timestamp_path)
        pressure_df = pd.read_csv(pressure_path)
        diameter_df = pd.read_csv(diameter_path)
        
        print(f"Loaded data for Subject {subject_number}:")
        print(f"  Timestamps: {len(timestamps_df)} rows")
        print(f"  Pressure: {len(pressure_df)} rows")
        print(f"  Diameter: {len(diameter_df)} rows")
        
        # Konversi timestamps ke datetime untuk timestamps_df
        if 'timestamps' in timestamps_df.columns:
            timestamps_df['timestamps'] = pd.to_datetime(timestamps_df['timestamps'])
        elif 'timestamp' in timestamps_df.columns:
            timestamps_df['timestamps'] = pd.to_datetime(timestamps_df['timestamp'])
            timestamps_df = timestamps_df.rename(columns={'timestamp': 'timestamps'})
            
        # Konversi timestamps ke datetime untuk pressure_df
        if 'timestamps' in pressure_df.columns:
            pressure_df['timestamps'] = pd.to_datetime(pressure_df['timestamps'])
        elif 'timestamp' in pressure_df.columns:
            pressure_df['timestamps'] = pd.to_datetime(pressure_df['timestamp'])
            pressure_df = pressure_df.rename(columns={'timestamp': 'timestamps'})
        
        # Merge data diameter dengan timestamps berdasarkan frame
        synced_data = pd.merge(timestamps_df, diameter_df, left_on='frame', right_on='Frame', how='outer')
        
        # Interpolasi data tekanan ke timestamps video
        if len(pressure_df) > 1:
            pressure_interpolator = interp1d(pressure_df['timestamps'].astype(np.int64), 
                                           pressure_df['pressure'], 
                                           bounds_error=False,
                                           fill_value="extrapolate")
                                           
            synced_data['pressure'] = pressure_interpolator(synced_data['timestamps'].astype(np.int64))
        else:
            synced_data['pressure'] = np.nan
        
        # Simpan hasil
        output_path = f"synced_data_subject{subject_number}.csv"
        synced_data.to_csv(output_path, index=False)
        
        # Visualisasi
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Plot diameter
        ax1.plot(synced_data['timestamps'], synced_data['Diameter (mm)'], 'b-', label='Diameter')
        ax1.set_ylabel('Diameter (mm)')
        ax1.set_title(f'Diameter dan Tekanan vs Waktu - Subjek {subject_number}')
        ax1.grid(True)
        ax1.legend()
        
        # Plot tekanan
        ax2.plot(synced_data['timestamps'], synced_data['pressure'], 'r-', label='Pressure')
        ax2.set_ylabel('Pressure (mmHg)')
        ax2.set_xlabel('Time')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plot_path = f'synced_data_plot_subject{subject_number}.png'
        plt.savefig(plot_path)
        plt.show()
        
        print(f"Data tersinkronisasi berhasil disimpan di: {output_path}")
        print(f"Plot disimpan di: {plot_path}")
        
        return synced_data
        
    except FileNotFoundError as e:
        print(f"Error: File tidak ditemukan - {str(e)}")
        return None
    except Exception as e:
        print(f"Error: Terjadi kesalahan - {str(e)}")
        print(f"Detail error: {str(e)}")
        return None

def process_all_subjects():
    """
    Proses sinkronisasi untuk semua subjek (1-7)
    """
    results = {}
    success_count = 0
    
    for subject in range(1, 8):
        print(f"\n{'='*50}")
        print(f"Memproses Subjek {subject}...")
        print(f"{'='*50}")
        
        result = sync_pressure_with_image_data(subject)
        if result is not None:
            results[f"subject_{subject}"] = result
            success_count += 1
            print(f"[SUCCESS] Sinkronisasi data Subjek {subject} berhasil")
        else:
            print(f"[ERROR] Sinkronisasi data Subjek {subject} gagal")
    
    print(f"\n{'='*50}")
    print(f"RINGKASAN PROSES")
    print(f"{'='*50}")
    print(f"Total subjek diproses: 7")
    print(f"Berhasil: {success_count}")
    print(f"Gagal: {7 - success_count}")
    
    return results

def analyze_synced_data(all_synced_data):
    """
    Analisis hasil sinkronisasi semua subjek
    
    Args:
        all_synced_data (dict): Dictionary berisi data tersinkronisasi semua subjek
    """
    if not all_synced_data:
        print("Tidak ada data tersinkronisasi untuk dianalisis.")
        return
    
    print(f"\n{'='*60}")
    print("ANALISIS DATA TERSINKRONISASI")
    print(f"{'='*60}")
    
    for subject_key, data in all_synced_data.items():
        print(f"\n{subject_key.upper().replace('_', ' ')}:")
        print(f"  [INFO] Jumlah frame: {len(data)}")
        
        # Analisis diameter
        diameter_data = data['Diameter (mm)'].dropna()
        if len(diameter_data) > 0:
            print(f"  📏 Diameter:")
            print(f"    - Range: {diameter_data.min():.2f} - {diameter_data.max():.2f} mm")
            print(f"    - Mean: {diameter_data.mean():.2f} mm")
            print(f"    - Std: {diameter_data.std():.2f} mm")
        
        # Analisis tekanan
        pressure_data = data['pressure'].dropna()
        if len(pressure_data) > 0:
            print(f"  🩺 Tekanan:")
            print(f"    - Range: {pressure_data.min():.2f} - {pressure_data.max():.2f} mmHg")
            print(f"    - Mean: {pressure_data.mean():.2f} mmHg")
            print(f"    - Std: {pressure_data.std():.2f} mmHg")
        
        # Korelasi diameter dan tekanan
        if len(diameter_data) > 0 and len(pressure_data) > 0:
            # Ambil data yang valid untuk keduanya
            valid_data = data.dropna(subset=['Diameter (mm)', 'pressure'])
            if len(valid_data) > 1:
                correlation = valid_data['Diameter (mm)'].corr(valid_data['pressure'])
                print(f"  🔗 Korelasi Diameter-Tekanan: {correlation:.3f}")

def create_summary_report(all_synced_data):
    """
    Buat laporan ringkasan dalam bentuk CSV
    
    Args:
        all_synced_data (dict): Dictionary berisi data tersinkronisasi semua subjek
    """
    if not all_synced_data:
        print("Tidak ada data untuk membuat laporan.")
        return
    
    summary_data = []
    
    for subject_key, data in all_synced_data.items():
        subject_num = subject_key.split('_')[1]
        
        # Hitung statistik
        diameter_data = data['Diameter (mm)'].dropna()
        pressure_data = data['pressure'].dropna()
        
        summary_row = {
            'Subject': subject_num,
            'Total_Frames': len(data),
            'Valid_Diameter_Frames': len(diameter_data),
            'Valid_Pressure_Frames': len(pressure_data)
        }
        
        if len(diameter_data) > 0:
            summary_row.update({
                'Diameter_Mean': diameter_data.mean(),
                'Diameter_Std': diameter_data.std(),
                'Diameter_Min': diameter_data.min(),
                'Diameter_Max': diameter_data.max()
            })
        
        if len(pressure_data) > 0:
            summary_row.update({
                'Pressure_Mean': pressure_data.mean(),
                'Pressure_Std': pressure_data.std(),
                'Pressure_Min': pressure_data.min(),
                'Pressure_Max': pressure_data.max()
            })
        
        # Korelasi
        valid_data = data.dropna(subset=['Diameter (mm)', 'pressure'])
        if len(valid_data) > 1:
            summary_row['Diameter_Pressure_Correlation'] = valid_data['Diameter (mm)'].corr(valid_data['pressure'])
        
        summary_data.append(summary_row)
    
    # Simpan ke CSV
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('synchronization_summary.csv', index=False)
    print(f"\n[LIST] Laporan ringkasan disimpan di: synchronization_summary.csv")
    
    return summary_df

def main():
    """
    Main function untuk menjalankan sinkronisasi data
    """
    print("[START] Memulai proses sinkronisasi data...")
    
    # Proses semua subjek
    all_synced_data = process_all_subjects()
    
    # Analisis hasil
    if all_synced_data:
        analyze_synced_data(all_synced_data)
        create_summary_report(all_synced_data)
        
        print(f"\n[SUCCESS] Proses sinkronisasi selesai!")
        print(f"📁 File output:")
        for subject_num in range(1, 8):
            csv_file = f"synced_data_subject{subject_num}.csv"
            plot_file = f"synced_data_plot_subject{subject_num}.png"
            if os.path.exists(csv_file):
                print(f"   - {csv_file}")
            if os.path.exists(plot_file):
                print(f"   - {plot_file}")
        print(f"   - synchronization_summary.csv")
    else:
        print("[ERROR] Tidak ada data yang berhasil disinkronisasi.")

if __name__ == "__main__":
    main()

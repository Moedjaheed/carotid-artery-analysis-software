"""
Advanced Analytics Module for Carotid Segmentation - Fixed Version
Provides detailed analysis, statistics, and visualization
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid threading issues
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks, savgol_filter
import cv2
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_diameter_column(dataframe):
    """
    Safely get the diameter column name from dataframe
    
    Args:
        dataframe (pd.DataFrame): DataFrame containing diameter data
        
    Returns:
        str or None: Column name for diameter data
    """
    if dataframe is None or dataframe.empty:
        return None
    
    # Check for common diameter column names
    possible_names = [
        'Diameter_mm',
        'Diameter (mm)', 
        'diameter',
        'Diameter',
        'DIAMETER',
        'diameter_mm'
    ]
    
    for name in possible_names:
        if name in dataframe.columns:
            return name
    
    # Try to find any column with 'diameter' in the name
    for col in dataframe.columns:
        if 'diameter' in col.lower():
            return col
    
    return None

class AdvancedAnalytics:
    """Advanced analytics for carotid artery data analysis"""
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.subjects_data = {}
        print("[SUCCESS] Advanced Analytics initialized")
    
    def load_subject_data(self, subject_number):
        """
        Load all available data for a specific subject
        
        Args:
            subject_number (int): Subject number (1, 2, 3, etc.)
            
        Returns:
            dict: Dictionary containing all subject data
        """
        subject_name = f"Subjek{subject_number}"
        subject_data = {
            'diameter_data': None,
            'timestamps': None,
            'pressure_data': None,
            'video_path': None,
            'segmentation_results': None
        }
        
        try:
            # Try to load diameter data from inference results
            diameter_path = f"inference_results/{subject_name}/{subject_name}_diameter_data.csv"
            if os.path.exists(diameter_path):
                subject_data['diameter_data'] = pd.read_csv(diameter_path)
                print(f"[SUCCESS] Loaded diameter data: {len(subject_data['diameter_data'])} frames")
            
            # Try enhanced diameter data with pressure
            enhanced_path = f"inference_results/{subject_name}/{subject_name}_diameter_data_with_pressure.csv"
            if os.path.exists(enhanced_path):
                subject_data['diameter_data'] = pd.read_csv(enhanced_path)
                print(f"[SUCCESS] Loaded enhanced diameter data: {len(subject_data['diameter_data'])} frames")
            
            # Load timestamps
            timestamp_path = f"data_uji/{subject_name}/timestamps.csv"
            if os.path.exists(timestamp_path):
                subject_data['timestamps'] = pd.read_csv(timestamp_path)
                print(f"[SUCCESS] Loaded timestamps: {len(subject_data['timestamps'])} entries")
            
            # Load pressure data
            pressure_path = f"data_uji/{subject_name}/subject{subject_number}.csv"
            if os.path.exists(pressure_path):
                subject_data['pressure_data'] = pd.read_csv(pressure_path)
                print(f"[SUCCESS] Loaded pressure data: {len(subject_data['pressure_data'])} entries")
            
            # Check for video file
            video_path = f"data_uji/{subject_name}/{subject_name}.mp4"
            if os.path.exists(video_path):
                subject_data['video_path'] = os.path.abspath(video_path)
                print(f"[SUCCESS] Video file found: {subject_data['video_path']}")
            
            # Check for segmentation results
            seg_video_path = f"inference_results/{subject_name}/{subject_name}_segmented_video.mp4"
            if os.path.exists(seg_video_path):
                subject_data['segmentation_results'] = os.path.abspath(seg_video_path)
                print(f"[SUCCESS] Segmentation results found: {subject_data['segmentation_results']}")
                
        except Exception as e:
            print(f"[WARN] Error loading subject {subject_number} data: {str(e)}")
        
        return subject_data
    
    def calculate_statistics(self, diameter_data):
        """
        Calculate comprehensive statistics for diameter data
        
        Args:
            diameter_data (pd.DataFrame): Diameter data
            
        Returns:
            dict: Dictionary of statistics
        """
        if diameter_data is None or len(diameter_data) == 0:
            return {}
        
        # Get diameter column safely
        diameter_col = get_diameter_column(diameter_data)
        if diameter_col is None:
            print("[ERROR] No diameter column found in data")
            return {}
        
        diameters = diameter_data[diameter_col].dropna()
        
        if len(diameters) == 0:
            return {}
        
        # Basic statistics
        stats_dict = {
            'count': len(diameters),
            'mean': float(diameters.mean()),
            'median': float(diameters.median()),
            'std': float(diameters.std()),
            'min': float(diameters.min()),
            'max': float(diameters.max()),
            'q25': float(diameters.quantile(0.25)),
            'q75': float(diameters.quantile(0.75)),
            'range': float(diameters.max() - diameters.min()),
            'cv': float((diameters.std() / diameters.mean()) * 100) if diameters.mean() != 0 else 0,
            'skewness': float(stats.skew(diameters)),
            'kurtosis': float(stats.kurtosis(diameters)),
            'total_frames': len(diameters),
            'sampling_rate_fps': 30,  # Assuming 30 FPS
            'duration_seconds': len(diameters) / 30,
        }
        
        # Enhanced statistics - estimate systolic/diastolic from percentiles
        try:
            # Smooth the data for better peak detection
            smoothed = savgol_filter(diameters, min(51, len(diameters)//4 if len(diameters) > 100 else 5), 3)
            
            # Use percentiles as rough estimates for systolic/diastolic
            stats_dict['estimated_systolic'] = float(diameters.quantile(0.9))  # 90th percentile
            stats_dict['estimated_diastolic'] = float(diameters.quantile(0.1))  # 10th percentile
            stats_dict['pulse_pressure_mm'] = stats_dict['estimated_systolic'] - stats_dict['estimated_diastolic']
            
        except Exception as e:
            print(f"[WARN] Error in enhanced statistics: {str(e)}")
            stats_dict['estimated_systolic'] = float(diameters.max())
            stats_dict['estimated_diastolic'] = float(diameters.min())
            stats_dict['pulse_pressure_mm'] = stats_dict['estimated_systolic'] - stats_dict['estimated_diastolic']
        
        return stats_dict
    
    def analyze_cardiac_cycles(self, diameter_data):
        """
        Analyze cardiac cycles in diameter data
        
        Args:
            diameter_data (pd.DataFrame): Diameter data
            
        Returns:
            dict: Cardiac cycle analysis results
        """
        if diameter_data is None or len(diameter_data) == 0:
            return {}
        
        # Get diameter column safely
        diameter_col = get_diameter_column(diameter_data)
        if diameter_col is None:
            return {}
        
        diameters = diameter_data[diameter_col].dropna()
        
        if len(diameters) < 100:  # Need sufficient data
            return {}
        
        try:
            # Smooth the data
            window_size = min(51, len(diameters)//10 if len(diameters) > 500 else 11)
            if window_size % 2 == 0:
                window_size += 1
            
            smoothed = savgol_filter(diameters, window_size, 3)
            
            # Find peaks (systolic) and troughs (diastolic)
            peaks, _ = find_peaks(smoothed, height=diameters.quantile(0.6), distance=20)
            troughs, _ = find_peaks(-smoothed, height=-diameters.quantile(0.4), distance=20)
            
            # Calculate cardiac cycle metrics
            cycles = {}
            
            if len(peaks) > 1:
                cycle_lengths = np.diff(peaks)
                cycles['num_cycles'] = len(peaks) - 1
                cycles['avg_cycle_length'] = float(np.mean(cycle_lengths))
                cycles['cycle_length_std'] = float(np.std(cycle_lengths))
                
                # Estimate heart rate (assuming 30 FPS)
                avg_cycle_seconds = cycles['avg_cycle_length'] / 30
                cycles['heart_rate_estimate'] = 60 / avg_cycle_seconds if avg_cycle_seconds > 0 else 0
                
                # Rhythm regularity (lower CV = more regular)
                cv_cycles = (cycles['cycle_length_std'] / cycles['avg_cycle_length']) * 100
                cycles['rhythm_regularity'] = max(0, 100 - cv_cycles)
                
            else:
                cycles = {
                    'num_cycles': 0,
                    'avg_cycle_length': 0,
                    'cycle_length_std': 0,
                    'heart_rate_estimate': 0,
                    'rhythm_regularity': 0
                }
            
            return cycles
            
        except Exception as e:
            print(f"[WARN] Error in cardiac cycle analysis: {str(e)}")
            return {}
    
    def assess_data_quality(self, subject_data):
        """
        Assess the quality of the data
        
        Args:
            subject_data (dict): Subject data dictionary
            
        Returns:
            dict: Data quality assessment
        """
        quality = {
            'overall_score': 0,
            'issues': [],
            'strengths': []
        }
        
        try:
            if subject_data['diameter_data'] is not None:
                diameter_data = subject_data['diameter_data']
                
                # Get diameter column safely
                diameter_col = get_diameter_column(diameter_data)
                if diameter_col is None:
                    quality['issues'].append("No diameter column found in data")
                    return quality
                
                # Check for missing values
                missing_pct = diameter_data[diameter_col].isna().mean() * 100
                if missing_pct < 5:
                    quality['strengths'].append(f"Low missing data rate: {missing_pct:.1f}%")
                    quality['overall_score'] += 25
                elif missing_pct < 15:
                    quality['issues'].append(f"Moderate missing data: {missing_pct:.1f}%")
                    quality['overall_score'] += 15
                else:
                    quality['issues'].append(f"High missing data rate: {missing_pct:.1f}%")
                
                # Check for outliers
                diameters = diameter_data[diameter_col].dropna()
                if len(diameters) > 0:
                    Q1 = diameters.quantile(0.25)
                    Q3 = diameters.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = diameters[(diameters < Q1 - 1.5*IQR) | (diameters > Q3 + 1.5*IQR)]
                    outlier_pct = len(outliers) / len(diameters) * 100
                    
                    if outlier_pct < 5:
                        quality['strengths'].append(f"Low outlier rate: {outlier_pct:.1f}%")
                        quality['overall_score'] += 25
                    elif outlier_pct < 10:
                        quality['issues'].append(f"Moderate outliers: {outlier_pct:.1f}%")
                        quality['overall_score'] += 15
                    else:
                        quality['issues'].append(f"High outlier rate: {outlier_pct:.1f}%")
                
                # Check data consistency
                if diameters.std() / diameters.mean() < 0.3:
                    quality['strengths'].append("Good data consistency (low CV)")
                    quality['overall_score'] += 25
                elif diameters.std() / diameters.mean() < 0.5:
                    quality['issues'].append("Moderate data variability")
                    quality['overall_score'] += 15
                else:
                    quality['issues'].append("High data variability")
            
            # Check for additional data availability
            if subject_data['pressure_data'] is not None:
                quality['strengths'].append("Pressure data available for enhanced analysis")
                quality['overall_score'] += 25
            
            if subject_data['timestamps'] is not None:
                quality['strengths'].append("Timestamp data available for temporal analysis")
                quality['overall_score'] += 25
                
        except Exception as e:
            quality['issues'].append(f"Error in quality assessment: {str(e)}")
            print(f"[WARN] Error in quality assessment: {str(e)}")
        
        return quality

    def generate_comprehensive_report(self, subject_number):
        """
        Generate comprehensive analysis report for a subject
        
        Args:
            subject_number (int): Subject number
            
        Returns:
            dict: Comprehensive report
        """
        print(f"[SEARCH] Generating comprehensive report for Subject {subject_number}...")
        
        # Load subject data
        subject_data = self.load_subject_data(subject_number)
        
        # Calculate statistics and quality
        stats = self.calculate_statistics(subject_data['diameter_data'])
        quality = self.assess_data_quality(subject_data)
        cardiac_cycles = self.analyze_cardiac_cycles(subject_data['diameter_data'])
        
        # Data availability check
        data_availability = {
            'diameter_data': subject_data['diameter_data'] is not None,
            'timestamps': subject_data['timestamps'] is not None,
            'pressure_data': subject_data['pressure_data'] is not None,
            'video_original': subject_data['video_path'] is not None,
            'segmentation_results': subject_data['segmentation_results'] is not None
        }
        
        # Create comprehensive report
        report = {
            'subject_number': subject_number,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_availability': data_availability,
            'basic_statistics': stats,
            'cardiac_cycles': cardiac_cycles,
            'data_quality': quality,
            'recommendations': self.generate_recommendations(stats, quality)
        }
        
        return report
    
    def generate_recommendations(self, stats, quality):
        """
        Generate recommendations based on analysis
        
        Args:
            stats (dict): Statistical data
            quality (dict): Quality assessment
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        try:
            if quality['overall_score'] < 50:
                recommendations.append("[WARN] Data quality is below acceptable threshold. Consider recalibration.")
            
            if stats and stats.get('cv', 0) > 30:
                recommendations.append("[INFO] High variability detected. Check for measurement artifacts.")
            
            if quality['issues']:
                recommendations.append("[SEARCH] Address identified data quality issues before clinical interpretation.")
            
            if stats and stats.get('count', 0) < 100:
                recommendations.append("📏 Limited data points. Consider longer recording for better analysis.")
            
            if quality['overall_score'] > 80:
                recommendations.append("[SUCCESS] Excellent data quality. Results are reliable for clinical analysis.")
                
        except Exception as e:
            recommendations.append(f"[ERROR] Error generating recommendations: {str(e)}")
        
        return recommendations

def create_analytics_gui():
    """Create GUI for advanced analytics"""
    root = tk.Tk()
    root.title("Advanced Carotid Analytics")
    root.geometry("800x600")
    
    analytics = AdvancedAnalytics()
    
    def run_analysis():
        try:
            subject_num = int(subject_var.get())
            print(f"[SEARCH] Generating comprehensive report for Subject {subject_num}...")
            
            # Load subject data
            subject_data = analytics.load_subject_data(subject_num)
            
            if subject_data['diameter_data'] is None:
                messagebox.showerror("Error", f"No diameter data found for Subject {subject_num}")
                return
            
            # Calculate statistics
            stats = analytics.calculate_statistics(subject_data['diameter_data'])
            quality = analytics.assess_data_quality(subject_data)
            
            # Display results
            result_text.delete(1.0, tk.END)
            
            result_text.insert(tk.END, f"=== ANALYSIS REPORT FOR SUBJECT {subject_num} ===\\n\\n")
            
            # Data Quality
            result_text.insert(tk.END, f"DATA QUALITY SCORE: {quality['overall_score']}/100\\n")
            if quality['strengths']:
                result_text.insert(tk.END, "\\nSTRENGTHS:\\n")
                for strength in quality['strengths']:
                    result_text.insert(tk.END, f"[SUCCESS] {strength}\\n")
            
            if quality['issues']:
                result_text.insert(tk.END, "\\nISSUES:\\n")
                for issue in quality['issues']:
                    result_text.insert(tk.END, f"[WARN] {issue}\\n")
            
            # Basic Statistics
            if stats:
                result_text.insert(tk.END, "\\n=== DIAMETER STATISTICS ===\\n")
                result_text.insert(tk.END, f"Count: {stats['count']} measurements\\n")
                result_text.insert(tk.END, f"Mean: {stats['mean']:.3f} mm\\n")
                result_text.insert(tk.END, f"Std: {stats['std']:.3f} mm\\n")
                result_text.insert(tk.END, f"Range: {stats['min']:.3f} - {stats['max']:.3f} mm\\n")
                result_text.insert(tk.END, f"CV: {stats['cv']:.1f}%\\n")
            
            messagebox.showinfo("Success", f"Analysis completed for Subject {subject_num}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    # GUI Elements
    ttk.Label(root, text="Advanced Carotid Analytics", font=("Arial", 16, "bold")).pack(pady=10)
    
    frame = ttk.Frame(root)
    frame.pack(pady=10)
    
    ttk.Label(frame, text="Select Subject:").pack(side=tk.LEFT)
    subject_var = tk.StringVar(value="1")
    ttk.Spinbox(frame, from_=1, to=10, textvariable=subject_var, width=5).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame, text="Run Analysis", command=run_analysis).pack(side=tk.LEFT, padx=5)
    
    # Results area
    result_frame = ttk.Frame(root)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    result_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10))
    scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_text.yview)
    result_text.configure(yscrollcommand=scrollbar.set)
    
    result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    return root

def main():
    """Main function for standalone testing"""
    root = create_analytics_gui()
    root.mainloop()

if __name__ == "__main__":
    main()

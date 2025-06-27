"""
Batch Processing Utility for Carotid Segmentation
Processes multiple subjects and generates comparative analysis
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
from advanced_analytics import AdvancedAnalytics

class BatchProcessor:
    """Batch processing utility for multiple subjects"""
    
    def __init__(self):
        """Initialize batch processor"""
        self.base_path = r"D:\Ridho\TA\fix banget"
        self.analytics = AdvancedAnalytics()
        self.results = {}
        
    def process_all_subjects(self, subjects=None):
        """
        Process all subjects or specified list
        
        Args:
            subjects (list): List of subject numbers to process, None for all (1-7)
            
        Returns:
            dict: Results for all processed subjects
        """
        if subjects is None:
            subjects = list(range(1, 8))  # Subjects 1-7
        
        print(f"🔄 Starting batch processing for subjects: {subjects}")
        
        all_results = {}
        
        for subject_num in subjects:
            print(f"\n[INFO] Processing Subject {subject_num}...")
            try:
                # Generate comprehensive report for this subject
                report = self.analytics.generate_comprehensive_report(subject_num)
                
                if report and report['basic_statistics']:
                    all_results[subject_num] = report
                    print(f"[SUCCESS] Subject {subject_num} processed successfully")
                else:
                    print(f"[WARN] Subject {subject_num} - insufficient data")
                    all_results[subject_num] = {'error': 'Insufficient data'}
                    
            except Exception as e:
                print(f"[ERROR] Error processing Subject {subject_num}: {str(e)}")
                all_results[subject_num] = {'error': str(e)}
        
        self.results = all_results
        return all_results
    
    def create_comparative_analysis(self, results=None):
        """
        Create comparative analysis across all subjects
        
        Args:
            results (dict): Results dictionary, uses self.results if None
            
        Returns:
            dict: Comparative analysis results
        """
        if results is None:
            results = self.results
        
        if not results:
            print("[ERROR] No results available for comparative analysis")
            return {}
        
        print("[CHART] Creating comparative analysis...")
        
        # Extract data for comparison
        comparison_data = {
            'subjects': [],
            'mean_diameter': [],
            'std_diameter': [],
            'cv_diameter': [],
            'heart_rate': [],
            'quality_score': [],
            'data_available': [],
            'cycle_count': [],
            'pulse_pressure': []
        }
        
        for subject_num, report in results.items():
            if 'error' in report:
                continue
                
            comparison_data['subjects'].append(f"Subject {subject_num}")
            
            # Basic statistics
            stats = report.get('basic_statistics', {})
            comparison_data['mean_diameter'].append(stats.get('mean', np.nan))
            comparison_data['std_diameter'].append(stats.get('std', np.nan))
            comparison_data['cv_diameter'].append(stats.get('cv', np.nan))
            comparison_data['pulse_pressure'].append(stats.get('pulse_pressure_mm', np.nan))
            
            # Cardiac cycles
            cycles = report.get('cardiac_cycles', {})
            comparison_data['heart_rate'].append(cycles.get('heart_rate_estimate', np.nan))
            comparison_data['cycle_count'].append(cycles.get('num_cycles', 0))
            
            # Data quality
            quality = report.get('data_quality', {})
            comparison_data['quality_score'].append(quality.get('overall_score', 0))
            
            # Data availability
            availability = report.get('data_availability', {})
            available_count = sum([
                availability.get('diameter_data', False),
                availability.get('timestamps', False),
                availability.get('pressure_data', False),
                availability.get('video_original', False),
                availability.get('segmentation_results', False)
            ])
            comparison_data['data_available'].append(available_count)
        
        # Create DataFrame for analysis
        df = pd.DataFrame(comparison_data)
        
        # Calculate summary statistics
        summary_stats = {
            'total_subjects_analyzed': len(df),
            'subjects_with_complete_data': (df['data_available'] == 5).sum(),
            'average_quality_score': df['quality_score'].mean(),
            'diameter_stats': {
                'mean_across_subjects': df['mean_diameter'].mean(),
                'std_across_subjects': df['mean_diameter'].std(),
                'range': [df['mean_diameter'].min(), df['mean_diameter'].max()]
            },
            'heart_rate_stats': {
                'mean_hr': df['heart_rate'].mean(),
                'std_hr': df['heart_rate'].std(),
                'range_hr': [df['heart_rate'].min(), df['heart_rate'].max()]
            },
            'data_quality_distribution': {
                'excellent': (df['quality_score'] >= 80).sum(),
                'good': ((df['quality_score'] >= 60) & (df['quality_score'] < 80)).sum(),
                'fair': ((df['quality_score'] >= 40) & (df['quality_score'] < 60)).sum(),
                'poor': (df['quality_score'] < 40).sum()
            }
        }
        
        comparative_results = {
            'summary_statistics': summary_stats,
            'detailed_data': df,
            'individual_reports': results,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return comparative_results
    
    def create_comparative_visualization(self, comparative_results, save_path=None):
        """
        Create comprehensive visualization comparing all subjects
        
        Args:
            comparative_results (dict): Results from create_comparative_analysis
            save_path (str): Optional path to save the figure
            
        Returns:
            matplotlib.figure.Figure: The created figure
        """
        if not comparative_results or 'detailed_data' not in comparative_results:
            print("[ERROR] No comparative data available for visualization")
            return None
        
        df = comparative_results['detailed_data']
        
        if df.empty:
            print("[ERROR] No valid data for visualization")
            return None
        
        # Set up the figure
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('Comprehensive Comparative Analysis - All Subjects', fontsize=20, fontweight='bold')
        
        # Set style
        plt.style.use('seaborn-v0_8')
        colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
        
        # 1. Mean diameter comparison
        ax1 = plt.subplot(3, 4, 1)
        bars = ax1.bar(df['subjects'], df['mean_diameter'], color=colors, alpha=0.8)
        ax1.set_title('Mean Diameter Comparison', fontweight='bold')
        ax1.set_ylabel('Diameter (mm)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, df['mean_diameter']):
            if not np.isnan(value):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Coefficient of variation comparison
        ax2 = plt.subplot(3, 4, 2)
        bars = ax2.bar(df['subjects'], df['cv_diameter'], color=colors, alpha=0.8)
        ax2.set_title('Measurement Variability (CV)', fontweight='bold')
        ax2.set_ylabel('CV (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, df['cv_diameter']):
            if not np.isnan(value):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 3. Heart rate comparison
        ax3 = plt.subplot(3, 4, 3)
        valid_hr = ~df['heart_rate'].isna()
        if valid_hr.any():
            bars = ax3.bar(df.loc[valid_hr, 'subjects'], df.loc[valid_hr, 'heart_rate'], 
                          color=np.array(colors)[valid_hr], alpha=0.8)
            ax3.set_title('Estimated Heart Rate', fontweight='bold')
            ax3.set_ylabel('HR (bpm)')
            ax3.tick_params(axis='x', rotation=45)
            
            for bar, value in zip(bars, df.loc[valid_hr, 'heart_rate']):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        # 4. Data quality scores
        ax4 = plt.subplot(3, 4, 4)
        bars = ax4.bar(df['subjects'], df['quality_score'], color=colors, alpha=0.8)
        ax4.set_title('Data Quality Scores', fontweight='bold')
        ax4.set_ylabel('Quality Score (%)')
        ax4.set_ylim(0, 100)
        ax4.tick_params(axis='x', rotation=45)
        
        # Add quality level lines
        ax4.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Excellent')
        ax4.axhline(y=60, color='orange', linestyle='--', alpha=0.7, label='Good')
        ax4.axhline(y=40, color='red', linestyle='--', alpha=0.7, label='Fair')
        ax4.legend(fontsize=8)
        
        for bar, value in zip(bars, df['quality_score']):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        # 5. Pulse pressure comparison
        ax5 = plt.subplot(3, 4, 5)
        valid_pp = ~df['pulse_pressure'].isna()
        if valid_pp.any():
            bars = ax5.bar(df.loc[valid_pp, 'subjects'], df.loc[valid_pp, 'pulse_pressure'], 
                          color=np.array(colors)[valid_pp], alpha=0.8)
            ax5.set_title('Pulse Pressure', fontweight='bold')
            ax5.set_ylabel('Pulse Pressure (mm)')
            ax5.tick_params(axis='x', rotation=45)
            
            for bar, value in zip(bars, df.loc[valid_pp, 'pulse_pressure']):
                ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 6. Data availability heatmap
        ax6 = plt.subplot(3, 4, 6)
        availability_matrix = []
        availability_labels = ['Diameter', 'Timestamps', 'Pressure', 'Video', 'Segmentation']
        
        for subject_num in range(1, len(df) + 1):
            if subject_num in comparative_results['individual_reports']:
                report = comparative_results['individual_reports'][subject_num]
                if 'data_availability' in report:
                    avail = report['data_availability']
                    row = [
                        1 if avail.get('diameter_data', False) else 0,
                        1 if avail.get('timestamps', False) else 0,
                        1 if avail.get('pressure_data', False) else 0,
                        1 if avail.get('video_original', False) else 0,
                        1 if avail.get('segmentation_results', False) else 0
                    ]
                    availability_matrix.append(row)
        
        if availability_matrix:
            sns.heatmap(np.array(availability_matrix).T, 
                       xticklabels=[f'S{i+1}' for i in range(len(availability_matrix))],
                       yticklabels=availability_labels,
                       cmap='RdYlGn', annot=True, fmt='d', cbar_kws={'label': 'Available'},
                       ax=ax6)
            ax6.set_title('Data Availability Matrix', fontweight='bold')
        
        # 7. Diameter distribution comparison (box plot)
        ax7 = plt.subplot(3, 4, 7)
        diameter_data = []
        subject_labels = []
        
        for subject_num, report in comparative_results['individual_reports'].items():
            if 'error' not in report and 'basic_statistics' in report:
                # Get diameter data for this subject
                subject_data = self.analytics.load_subject_data(subject_num)
                if subject_data['diameter_data'] is not None:
                    diams = subject_data['diameter_data']['Diameter_mm'].dropna()
                    if len(diams) > 0:
                        diameter_data.append(diams.values)
                        subject_labels.append(f'S{subject_num}')
        
        if diameter_data:
            ax7.boxplot(diameter_data, labels=subject_labels, patch_artist=True)
            ax7.set_title('Diameter Distribution Comparison', fontweight='bold')
            ax7.set_ylabel('Diameter (mm)')
            ax7.tick_params(axis='x', rotation=45)
        
        # 8. Quality vs Heart Rate scatter
        ax8 = plt.subplot(3, 4, 8)
        valid_both = ~(df['heart_rate'].isna() | df['quality_score'].isna())
        if valid_both.any():
            scatter = ax8.scatter(df.loc[valid_both, 'heart_rate'], 
                                 df.loc[valid_both, 'quality_score'],
                                 c=np.array(colors)[valid_both], s=100, alpha=0.8)
            ax8.set_title('Quality vs Heart Rate', fontweight='bold')
            ax8.set_xlabel('Heart Rate (bpm)')
            ax8.set_ylabel('Quality Score (%)')
            
            # Add subject labels
            for i, (hr, qs, subj) in enumerate(zip(df.loc[valid_both, 'heart_rate'],
                                                  df.loc[valid_both, 'quality_score'],
                                                  df.loc[valid_both, 'subjects'])):
                ax8.annotate(subj.split()[1], (hr, qs), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        # 9. Statistical summary table
        ax9 = plt.subplot(3, 4, 9)
        ax9.axis('off')
        
        summary = comparative_results['summary_statistics']
        table_data = [
            ['Total Subjects', f"{summary['total_subjects_analyzed']}"],
            ['Complete Data', f"{summary['subjects_with_complete_data']}"],
            ['Avg Quality', f"{summary['average_quality_score']:.1f}%"],
            ['Mean Diameter', f"{summary['diameter_stats']['mean_across_subjects']:.2f}±{summary['diameter_stats']['std_across_subjects']:.2f}mm"],
            ['Mean HR', f"{summary['heart_rate_stats']['mean_hr']:.1f}±{summary['heart_rate_stats']['std_hr']:.1f}bpm"],
        ]
        
        table = ax9.table(cellText=table_data, colLabels=['Metric', 'Value'],
                         cellLoc='center', loc='center', bbox=[0.1, 0.1, 0.8, 0.8])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax9.set_title('Summary Statistics', fontweight='bold')
        
        # 10. Quality distribution pie chart
        ax10 = plt.subplot(3, 4, 10)
        quality_dist = summary['data_quality_distribution']
        labels = ['Excellent (≥80%)', 'Good (60-79%)', 'Fair (40-59%)', 'Poor (<40%)']
        sizes = [quality_dist['excellent'], quality_dist['good'], 
                quality_dist['fair'], quality_dist['poor']]
        colors_pie = ['green', 'orange', 'yellow', 'red']
        
        # Only include non-zero sizes
        non_zero = [(label, size, color) for label, size, color in zip(labels, sizes, colors_pie) if size > 0]
        if non_zero:
            labels_nz, sizes_nz, colors_nz = zip(*non_zero)
            ax10.pie(sizes_nz, labels=labels_nz, colors=colors_nz, autopct='%1.0f%%', startangle=90)
        ax10.set_title('Quality Score Distribution', fontweight='bold')
        
        # 11. Measurement consistency comparison
        ax11 = plt.subplot(3, 4, 11)
        bars = ax11.bar(df['subjects'], df['std_diameter'], color=colors, alpha=0.8)
        ax11.set_title('Measurement Standard Deviation', fontweight='bold')
        ax11.set_ylabel('Std Dev (mm)')
        ax11.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, df['std_diameter']):
            if not np.isnan(value):
                ax11.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                         f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 12. Processing completeness
        ax12 = plt.subplot(3, 4, 12)
        bars = ax12.bar(df['subjects'], df['data_available'], color=colors, alpha=0.8)
        ax12.set_title('Data Completeness', fontweight='bold')
        ax12.set_ylabel('Available Data Types (0-5)')
        ax12.set_ylim(0, 5)
        ax12.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, df['data_available']):
            ax12.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     f'{value}/5', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[SUCCESS] Comparative visualization saved to: {save_path}")
        
        return fig
    
    def export_results(self, comparative_results, export_format='json'):
        """
        Export results to file
        
        Args:
            comparative_results (dict): Results to export
            export_format (str): 'json', 'csv', or 'excel'
            
        Returns:
            str: Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format == 'json':
            filename = f"batch_analysis_results_{timestamp}.json"
            
            # Convert DataFrame to dict for JSON serialization
            export_data = comparative_results.copy()
            if 'detailed_data' in export_data:
                export_data['detailed_data'] = export_data['detailed_data'].to_dict('records')
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
        elif export_format == 'csv':
            filename = f"batch_analysis_summary_{timestamp}.csv"
            comparative_results['detailed_data'].to_csv(filename, index=False)
            
        elif export_format == 'excel':
            filename = f"batch_analysis_complete_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename) as writer:
                # Summary sheet
                summary_df = pd.DataFrame([comparative_results['summary_statistics']], 
                                        index=['Summary'])
                summary_df.to_excel(writer, sheet_name='Summary')
                
                # Detailed data sheet
                comparative_results['detailed_data'].to_excel(writer, 
                                                            sheet_name='Detailed_Data', 
                                                            index=False)
                
                # Individual reports sheet
                reports_data = []
                for subject, report in comparative_results['individual_reports'].items():
                    if 'error' not in report:
                        row = {'Subject': subject}
                        if 'basic_statistics' in report:
                            row.update(report['basic_statistics'])
                        reports_data.append(row)
                
                if reports_data:
                    reports_df = pd.DataFrame(reports_data)
                    reports_df.to_excel(writer, sheet_name='Individual_Stats', index=False)
        
        print(f"[SUCCESS] Results exported to: {filename}")
        return filename
    
    def run_complete_batch_analysis(self, subjects=None, export_formats=['json'], create_viz=True):
        """
        Run complete batch analysis pipeline
        
        Args:
            subjects (list): List of subjects to process
            export_formats (list): List of export formats ('json', 'csv', 'excel')
            create_viz (bool): Whether to create visualization
            
        Returns:
            dict: Complete analysis results
        """
        print("[START] Starting complete batch analysis pipeline...")
        
        # Step 1: Process all subjects
        results = self.process_all_subjects(subjects)
        
        if not results:
            print("[ERROR] No subjects processed successfully")
            return {}
        
        # Step 2: Create comparative analysis
        comparative_results = self.create_comparative_analysis(results)
        
        # Step 3: Create visualization
        if create_viz:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_path = f"batch_analysis_visualization_{timestamp}.png"
            fig = self.create_comparative_visualization(comparative_results, viz_path)
            if fig:
                plt.close(fig)  # Close to free memory
        
        # Step 4: Export results
        exported_files = []
        for fmt in export_formats:
            try:
                filename = self.export_results(comparative_results, fmt)
                exported_files.append(filename)
            except Exception as e:
                print(f"[WARN] Failed to export as {fmt}: {str(e)}")
        
        # Step 5: Generate summary report
        self.generate_summary_report(comparative_results)
        
        print("[SUCCESS] Complete batch analysis finished!")
        print(f"📁 Exported files: {exported_files}")
        
        return comparative_results
    
    def generate_summary_report(self, comparative_results):
        """
        Generate a human-readable summary report
        
        Args:
            comparative_results (dict): Analysis results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_analysis_summary_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("CAROTID SEGMENTATION - BATCH ANALYSIS SUMMARY REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {comparative_results['timestamp']}\n\n")
            
            summary = comparative_results['summary_statistics']
            
            f.write("OVERVIEW\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total subjects analyzed: {summary['total_subjects_analyzed']}\n")
            f.write(f"Subjects with complete data: {summary['subjects_with_complete_data']}\n")
            f.write(f"Average data quality score: {summary['average_quality_score']:.1f}%\n\n")
            
            f.write("DIAMETER MEASUREMENTS\n")
            f.write("-" * 25 + "\n")
            diam_stats = summary['diameter_stats']
            f.write(f"Mean diameter across subjects: {diam_stats['mean_across_subjects']:.3f} ± {diam_stats['std_across_subjects']:.3f} mm\n")
            f.write(f"Diameter range: {diam_stats['range'][0]:.3f} - {diam_stats['range'][1]:.3f} mm\n\n")
            
            f.write("HEART RATE ANALYSIS\n")
            f.write("-" * 20 + "\n")
            hr_stats = summary['heart_rate_stats']
            f.write(f"Mean heart rate: {hr_stats['mean_hr']:.1f} ± {hr_stats['std_hr']:.1f} bpm\n")
            f.write(f"Heart rate range: {hr_stats['range_hr'][0]:.1f} - {hr_stats['range_hr'][1]:.1f} bpm\n\n")
            
            f.write("DATA QUALITY DISTRIBUTION\n")
            f.write("-" * 30 + "\n")
            quality_dist = summary['data_quality_distribution']
            f.write(f"Excellent (≥80%): {quality_dist['excellent']} subjects\n")
            f.write(f"Good (60-79%): {quality_dist['good']} subjects\n")
            f.write(f"Fair (40-59%): {quality_dist['fair']} subjects\n")
            f.write(f"Poor (<40%): {quality_dist['poor']} subjects\n\n")
            
            f.write("INDIVIDUAL SUBJECT SUMMARY\n")
            f.write("-" * 30 + "\n")
            
            df = comparative_results['detailed_data']
            for _, row in df.iterrows():
                f.write(f"{row['subjects']}:\n")
                f.write(f"  Mean diameter: {row['mean_diameter']:.3f} mm\n")
                f.write(f"  Measurement CV: {row['cv_diameter']:.1f}%\n")
                f.write(f"  Heart rate: {row['heart_rate']:.1f} bpm\n")
                f.write(f"  Quality score: {row['quality_score']:.0f}%\n")
                f.write(f"  Data completeness: {row['data_available']}/5\n\n")
        
        print(f"[DOCS] Summary report saved to: {filename}")

def main():
    """Main function for running batch processing"""
    print("🔄 Carotid Segmentation - Batch Processing Utility")
    print("=" * 50)
    
    # Create batch processor
    processor = BatchProcessor()
    
    # Run complete analysis
    try:
        results = processor.run_complete_batch_analysis(
            subjects=None,  # Process all subjects
            export_formats=['json', 'csv', 'excel'],
            create_viz=True
        )
        
        print("\n[SUCCESS] Batch processing completed successfully!")
        print(f"[INFO] Processed {len(results.get('individual_reports', {}))} subjects")
        
    except Exception as e:
        print(f"[ERROR] Error in batch processing: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()

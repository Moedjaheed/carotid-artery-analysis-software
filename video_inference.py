"""
Video Inference untuk Segmentasi Karotis
File untuk implementasi model ke data uji video, menghasilkan:
1. Video dengan overlay segmentasi
2. Plot diameter vs frame (PNG)
3. CSV data diameter per frame
"""

import os
# Set environment variable to avoid OpenMP conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import albumentations as A
from albumentations.pytorch import ToTensorV2
import pandas as pd
from scipy.interpolate import interp1d
import argparse

# Set device - try CUDA first, fallback to CPU if issues
try:
    if torch.cuda.is_available():
        device = torch.device('cuda')
        # Test CUDA with a simple operation
        test_tensor = torch.tensor([1.0]).cuda()
        _ = test_tensor + 1  # Test basic operation
        print(f"Using device: {device} (CUDA available and working)")
    else:
        device = torch.device('cpu')
        print(f"Using device: {device} (CUDA not available)")
except Exception as e:
    print(f"CUDA error detected: {e}")
    print("Falling back to CPU processing...")
    device = torch.device('cpu')
    print(f"Using device: {device} (CPU fallback)")

class UNetCompatible(nn.Module):
    """U-Net kompatibel dengan model yang tersimpan"""
    def __init__(self, n_channels=3, n_classes=1):  # Changed to 3 channels
        super(UNetCompatible, self).__init__()
        
        # Encoder layers (sesuai dengan model yang tersimpan)
        self.enc1 = nn.Sequential(
            nn.Conv2d(n_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        self.enc2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        self.enc3 = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.enc4 = nn.Sequential(
            nn.Conv2d(256, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        
        # Bottleneck
        self.bottleneck = nn.Sequential(
            nn.Conv2d(512, 1024, 3, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True),
            nn.Conv2d(1024, 1024, 3, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True)
        )
        
        # Decoder upconv layers
        self.upconv4 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.upconv3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.upconv2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.upconv1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        
        # Decoder conv layers
        self.dec4 = nn.Sequential(
            nn.Conv2d(1024, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        
        self.dec3 = nn.Sequential(
            nn.Conv2d(512, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.dec2 = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        self.dec1 = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        # Output layer
        self.out_conv = nn.Conv2d(64, n_classes, 1)
        
        # Max pooling
        self.pool = nn.MaxPool2d(2)

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        
        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))
        
        # Decoder
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)
        
        # Output
        out = self.out_conv(dec1)
        return out

class VideoProcessor:
    """Class untuk memproses video dengan model segmentasi"""
    
    def __init__(self, model_path):
        """
        Initialize VideoProcessor
        
        Args:
            model_path (str): Path ke model yang sudah ditraining
        """
        self.device = device
        self.model = UNetCompatible().to(self.device)
          # Load model dengan error handling
        if os.path.exists(model_path):
            try:
                print(f"Loading model from {model_path}...")
                print(f"Using device: {self.device}")
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
                print(f"[SUCCESS] Model loaded successfully from {model_path}")
            except Exception as e:
                print(f"[ERROR] Error loading model: {str(e)}")
                raise RuntimeError(f"Failed to load model: {str(e)}")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")        # Preprocessing transform (sesuai dengan training)
        self.transform = A.Compose([
            A.Resize(512, 512),
            A.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    def preprocess_frame(self, frame):
        """
        Preprocess frame untuk inference (sesuai dengan training)
        
        Args:
            frame: Frame dari video (numpy array)
            
        Returns:
            tensor: Preprocessed frame sebagai tensor
        """
        # Convert BGR to RGB (OpenCV uses BGR)
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif len(frame.shape) == 2:
            # Convert grayscale to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            frame_rgb = frame
          # Apply transform (resize + normalize)
        transformed = self.transform(image=frame_rgb)
        tensor_frame = transformed['image'].unsqueeze(0).to(self.device)
        
        return tensor_frame
    
    def predict_mask(self, frame):
        """
        Prediksi mask dari frame (sesuai dengan implementasi notebook)
        Optimized version with torch.no_grad() and CPU processing
        
        Args:
            frame: Input frame (BGR format dari OpenCV)
            
        Returns:
            numpy array: Predicted mask (binary, 0 atau 255)
        """
        original_size = (frame.shape[1], frame.shape[0])  # (width, height)
        
        with torch.no_grad():  # Disable gradient computation for faster inference
            # Preprocess frame
            tensor_frame = self.preprocess_frame(frame)
            
            # Model inference
            prediction = self.model(tensor_frame)
            prediction = prediction.squeeze().cpu().numpy()
            
            # Convert to binary mask
            binary_mask = (prediction > 0.5).astype(np.uint8) * 255
            
            # Resize back to original frame size
            mask_resized = cv2.resize(binary_mask, original_size)
            
            return mask_resized
    
    def calculate_diameter(self, mask, pixel_to_mm_ratio=0.1):
        """
        Hitung diameter dari mask
        
        Args:
            mask: Binary mask
            pixel_to_mm_ratio: Rasio konversi pixel ke mm
            
        Returns:
            float: Diameter dalam mm
        """
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate diameter using different methods
            # Method 1: Minimum enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            diameter_pixels = radius * 2
            
            # Method 2: Bounding rectangle width (alternative)
            # x, y, w, h = cv2.boundingRect(largest_contour)
            # diameter_pixels = max(w, h)
            
            # Convert to mm
            diameter_mm = diameter_pixels * pixel_to_mm_ratio
            return diameter_mm
        
        return 0.0
    def draw_overlay(self, frame, mask, diameter_mm=None):
        """
        Gambar overlay pada frame (implementasi sesuai notebook)
        
        Args:
            frame: Original frame (BGR)
            mask: Predicted mask (binary, 0 atau 255)
            diameter_mm: Diameter dalam mm (optional)
            
        Returns:
            numpy array: Frame dengan overlay transparan
        """
        # Create overlay dengan filled area transparan (sesuai notebook)
        overlay_color = (0, 255, 0)  # Green in BGR
        alpha = 0.4  # Transparansi
        
        # Buat mask berwarna
        colored_mask = np.zeros_like(frame, dtype=np.uint8)
        colored_mask[mask == 255] = overlay_color
        
        # Gabungkan mask dengan frame menggunakan transparansi
        overlay = cv2.addWeighted(colored_mask, alpha, frame, 1 - alpha, 0)
        
        # Tambahkan contour outline
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Gambar contour outline
            cv2.drawContours(overlay, contours, -1, (0, 255, 255), 2)  # Yellow outline
            
            # Gambar circle untuk diameter jika ada
            largest_contour = max(contours, key=cv2.contourArea)
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            center = (int(x), int(y))
            cv2.circle(overlay, center, int(radius), (255, 0, 0), 2)  # Blue circle
            cv2.circle(overlay, center, 2, (0, 0, 255), -1)  # Red center point
            
            # Tambahkan text diameter jika ada
            if diameter_mm is not None and diameter_mm > 0:
                text = f"Diameter: {diameter_mm:.2f} mm"
                cv2.putText(overlay, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return overlay
    
    def process_video_with_diameter(self, video_path, output_path, plot_path, csv_path):
        """
        Proses video dengan overlay segmentasi dan hitung diameter (sesuai notebook)
        Includes timestamp integration if available
        
        Args:
            video_path (str): Path ke video input
            output_path (str): Path untuk video output
            plot_path (str): Path untuk plot diameter
            csv_path (str): Path untuk file CSV
        """
        # Parameter Kalibrasi sesuai notebook
        depth_mm = 50               # Depth pengambilan citra (dalam mm)
        image_height_px = 1048      # Resolusi vertikal citra (dalam pixel)
        scale_mm_per_pixel = depth_mm / image_height_px  # Konversi pixel ke mm
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {video_path}")
        print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        print(f"Scale: {scale_mm_per_pixel:.6f} mm/pixel")
        
        # Try to load timestamp data for integration
        timestamp_data = None
        try:
            # Extract subject name from video path
            video_dir = os.path.dirname(video_path)
            subject_name = os.path.basename(video_dir)
            timestamps_csv_path = os.path.join("data_uji", subject_name, "timestamps.csv")
            
            if os.path.exists(timestamps_csv_path):
                timestamp_data = pd.read_csv(timestamps_csv_path)
                print(f"[OK] Found timestamp data: {len(timestamp_data)} entries")
                print(f"Timestamp columns: {list(timestamp_data.columns)}")
                
                # Ensure consistent column names
                if 'Frame Number' in timestamp_data.columns:
                    timestamp_data['Frame'] = timestamp_data['Frame Number']
                elif 'frame' in timestamp_data.columns:
                    timestamp_data['Frame'] = timestamp_data['frame']
                elif 'Frame' not in timestamp_data.columns:
                    # If no Frame column, create one based on index
                    timestamp_data['Frame'] = timestamp_data.index
                    
            else:
                print(f"[WARN] No timestamp data found at: {timestamps_csv_path}")
        except Exception as e:
            print(f"[WARN] Warning: Could not load timestamp data: {e}")
            timestamp_data = None
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
          # Lists to store data
        frame_diameters_mm = []
        frame_numbers = []
        
        frame_idx = 0
        
        print("Processing frames...")
        print(f"Total frames to process: {total_frames}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Predict mask
            mask = self.predict_mask(frame)
            
            # Calculate diameter menggunakan scale yang benar
            diameter_mm = self.calculate_diameter(mask, scale_mm_per_pixel)
            
            # Draw overlay
            overlay = self.draw_overlay(frame, mask, diameter_mm)
            
            # Store data
            if diameter_mm > 0:  # Only store valid measurements
                frame_diameters_mm.append(diameter_mm)
                frame_numbers.append(frame_idx)
            
            # Write frame
            out.write(overlay)
              # Enhanced progress display with percentage
            if frame_idx % 25 == 0 or frame_idx == total_frames - 1:  # More frequent updates
                progress_pct = (frame_idx + 1) / total_frames * 100
                remaining_frames = total_frames - (frame_idx + 1)
                
                # Create simple progress bar
                bar_length = 30
                filled_length = int(bar_length * (frame_idx + 1) // total_frames)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"[PROGRESS] {bar} {progress_pct:.1f}% ({frame_idx + 1}/{total_frames}) - Diameter: {diameter_mm:.2f}mm")
            
            frame_idx += 1
          # Release resources
        cap.release()
        out.release()
        print(f"Video saved to: {output_path}")        # Save CSV data with timestamp integration
        if frame_diameters_mm:
            # Prepare data for CSV
            csv_data = []
            
            # Create timestamp mapping if available
            timestamp_map = {}
            if timestamp_data is not None:
                print(f"Creating timestamp mapping from {len(timestamp_data)} timestamp entries...")
                
                # Try different column combinations
                frame_col = None
                timestamp_col = None
                
                # Find frame column
                if 'Frame' in timestamp_data.columns:
                    frame_col = 'Frame'
                elif 'Frame Number' in timestamp_data.columns:
                    frame_col = 'Frame Number'
                elif 'frame' in timestamp_data.columns:
                    frame_col = 'frame'
                
                # Find timestamp column
                if 'Timestamp' in timestamp_data.columns:
                    timestamp_col = 'Timestamp'
                elif 'timestamp' in timestamp_data.columns:
                    timestamp_col = 'timestamp'
                elif 'Time' in timestamp_data.columns:
                    timestamp_col = 'Time'
                
                if frame_col and timestamp_col:
                    for _, row in timestamp_data.iterrows():
                        try:
                            frame_num = int(row[frame_col])
                            timestamp = row[timestamp_col]
                            timestamp_map[frame_num] = timestamp
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not parse row {row.name}: {e}")
                    print(f"Created timestamp mapping for {len(timestamp_map)} frames")
                else:
                    print(f"Warning: Could not find appropriate columns. Available: {list(timestamp_data.columns)}")
                    print(f"Frame column: {frame_col}, Timestamp column: {timestamp_col}")
            
            # Write CSV with enhanced data
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                  # Header - include timestamp if available
                if timestamp_map:
                    writer.writerow(["Frame", "Diameter (mm)", "Timestamp"])
                    print("[OK] Creating CSV with Frame, Diameter, and Timestamp columns")
                else:
                    writer.writerow(["Frame", "Diameter (mm)"])
                    print("[WARN] Creating CSV with Frame and Diameter columns only (no timestamps)")
                  # Data rows
                for frame, diameter_mm in zip(frame_numbers, frame_diameters_mm):
                    if timestamp_map and frame in timestamp_map:
                        writer.writerow([frame, f"{diameter_mm:.4f}", timestamp_map[frame]])
                    else:
                        writer.writerow([frame, f"{diameter_mm:.4f}"])
            
            print(f"[OK] Diameter data saved to: {csv_path}")
            if timestamp_map:
                matched_timestamps = sum(1 for frame in frame_numbers if frame in timestamp_map)
                print(f"[INFO] Timestamp integration: {matched_timestamps}/{len(frame_numbers)} frames have timestamps")
                if matched_timestamps < len(frame_numbers):
                    print(f"[WARN] Some frames don't have corresponding timestamps")
            else:
                print("[WARN] No timestamp data integrated - check timestamp file format")
            
            # Create plot
            plt.figure(figsize=(12, 6))
            plt.plot(frame_numbers, frame_diameters_mm, marker='o', linestyle='-', markersize=3)
            plt.title("Diameter Arteri Karotis per Frame")
            plt.xlabel("Frame")
            plt.ylabel("Diameter (mm)")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Add statistics to plot
            avg_diameter = np.mean(frame_diameters_mm)
            std_diameter = np.std(frame_diameters_mm)
            min_diameter = np.min(frame_diameters_mm)
            max_diameter = np.max(frame_diameters_mm)
            
            stats_text = f'Statistics:\nMean: {avg_diameter:.2f} mm\nStd: {std_diameter:.2f} mm\nMin: {min_diameter:.2f} mm\nMax: {max_diameter:.2f} mm'
            plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.show()
            print(f"Plot saved to: {plot_path}")
            
            # Print summary
            print(f"\nProcessing Summary:")
            print(f"Total frames: {total_frames}")
            print(f"Frames with valid diameter: {len(frame_diameters_mm)}")
            print(f"Average diameter: {avg_diameter:.2f} mm")
            print(f"Diameter range: {min_diameter:.2f} - {max_diameter:.2f} mm")
            
        else:
            print("No valid diameter measurements detected.")
    
    def process_single_frame(self, frame_path, output_path):
        """
        Proses single frame untuk testing
        
        Args:
            frame_path (str): Path ke gambar
            output_path (str): Path output
        """
        # Load image
        frame = cv2.imread(frame_path)
        if frame is None:
            raise ValueError(f"Cannot load image: {frame_path}")
        
        # Predict mask
        mask = self.predict_mask(frame)
        
        # Calculate diameter
        diameter_mm = self.calculate_diameter(mask)
        
        # Draw overlay
        overlay = self.draw_overlay(frame, mask, diameter_mm)
        
        # Save result
        cv2.imwrite(output_path, overlay)
        print(f"Processed frame saved to: {output_path}")
        print(f"Detected diameter: {diameter_mm:.2f} mm")

    def load_and_sync_pressure_data(self, pressure_csv_path, timestamps_csv_path):
        """
        Load dan sinkronisasi data tekanan dengan timestamp
        
        Args:
            pressure_csv_path (str): Path ke file CSV data tekanan
            timestamps_csv_path (str): Path ke file CSV timestamp
            
        Returns:
            tuple: (pressure_data, timestamps_data) atau (None, None) jika error
        """
        try:
            # Load pressure data
            if os.path.exists(pressure_csv_path):
                pressure_df = pd.read_csv(pressure_csv_path)
                print(f"Loaded pressure data: {len(pressure_df)} entries")
                print(f"Pressure columns: {pressure_df.columns.tolist()}")
                
                # Rename columns for consistency
                if 'Sensor Value' in pressure_df.columns:
                    pressure_df = pressure_df.rename(columns={'Sensor Value': 'pressure'})
                if 'Timestamp (s)' in pressure_df.columns:
                    pressure_df = pressure_df.rename(columns={'Timestamp (s)': 'timestamp'})
                    
            else:
                print(f"Pressure data not found: {pressure_csv_path}")
                return None, None
            
            # Load timestamps
            if os.path.exists(timestamps_csv_path):
                timestamps_df = pd.read_csv(timestamps_csv_path)
                print(f"Loaded timestamps: {len(timestamps_df)} entries")
                print(f"Timestamp columns: {timestamps_df.columns.tolist()}")
                
                # Rename columns for consistency
                if 'Frame Number' in timestamps_df.columns:
                    timestamps_df = timestamps_df.rename(columns={'Frame Number': 'frame'})
                if 'Timestamp' in timestamps_df.columns:
                    timestamps_df = timestamps_df.rename(columns={'Timestamp': 'timestamp'})
                    
            else:
                print(f"Timestamps not found: {timestamps_csv_path}")
                return pressure_df, None
            
            return pressure_df, timestamps_df
            
        except Exception as e:
            print(f"Error loading pressure/timestamp data: {str(e)}")
            return None, None

    def process_video_with_pressure_integration(self, video_path, output_path, plot_path, csv_path, 
                                              pressure_csv_path=None, timestamps_csv_path=None):
        """
        Proses video dengan integrasi data tekanan
        
        Args:
            video_path (str): Path ke video input
            output_path (str): Path untuk video output
            plot_path (str): Path untuk plot diameter
            csv_path (str): Path untuk file CSV
            pressure_csv_path (str): Path ke file CSV data tekanan
            timestamps_csv_path (str): Path ke file CSV timestamp
        """
        # Load pressure and timestamp data
        pressure_df = None
        timestamps_df = None
        
        if pressure_csv_path and timestamps_csv_path:
            pressure_df, timestamps_df = self.load_and_sync_pressure_data(
                pressure_csv_path, timestamps_csv_path
            )
        
        # Process video normally first
        self.process_video_with_diameter(video_path, output_path, plot_path, csv_path)
          # If pressure data available, create enhanced analysis
        if pressure_df is not None:
            try:
                self.create_enhanced_analysis_with_pressure(
                    csv_path, pressure_df, timestamps_df, plot_path
                )
            except Exception as e:
                print(f"Warning: Could not create enhanced pressure analysis: {str(e)}")
    
    def create_enhanced_analysis_with_pressure(self, diameter_csv_path, pressure_df, timestamps_df, base_plot_path):
        """
        Buat analisis enhanced dengan data tekanan
        
        Args:
            diameter_csv_path (str): Path ke file CSV diameter yang sudah dibuat
            pressure_df (DataFrame): Data tekanan
            timestamps_df (DataFrame): Data timestamp
            base_plot_path (str): Base path untuk plot
        """
        try:
            # Load diameter data
            diameter_df = pd.read_csv(diameter_csv_path)
            print(f"Loaded diameter data for pressure integration: {len(diameter_df)} frames")
            print(f"Diameter CSV columns: {list(diameter_df.columns)}")
            
            # Prepare data for synchronization
            if timestamps_df is not None and pressure_df is not None:
                # Convert timestamps to consistent format
                if 'timestamp' in timestamps_df.columns and 'timestamp' in pressure_df.columns:
                    # Simple approach: interpolate pressure to match frame numbers
                    frame_count = len(diameter_df)
                    pressure_count = len(pressure_df)
                    
                    # Create interpolation function
                    pressure_indices = np.linspace(0, pressure_count-1, pressure_count)
                    frame_indices = np.linspace(0, pressure_count-1, frame_count)
                    
                    if len(pressure_df['pressure']) > 1:
                        pressure_interpolator = interp1d(
                            pressure_indices, 
                            pressure_df['pressure'], 
                            kind='linear', 
                            bounds_error=False, 
                            fill_value='extrapolate'
                        )
                        
                        # Interpolate pressure for each frame
                        interpolated_pressure = pressure_interpolator(frame_indices)
                        
                        # Add pressure to diameter data (preserving existing columns including timestamp)
                        diameter_df['pressure'] = interpolated_pressure
                        
                        # Save enhanced CSV with all columns preserved
                        enhanced_csv_path = diameter_csv_path.replace('.csv', '_with_pressure.csv')
                        diameter_df.to_csv(enhanced_csv_path, index=False)
                        
                        print(f"Enhanced CSV with pressure saved: {enhanced_csv_path}")
                        print(f"Enhanced CSV columns: {list(diameter_df.columns)}")
                        
                        # Verify timestamp preservation
                        if 'Timestamp' in diameter_df.columns:
                            valid_timestamps = diameter_df['Timestamp'].notna().sum()
                            print(f"Timestamps preserved: {valid_timestamps}/{len(diameter_df)} frames")
                        
                        # Create dual-axis plot
                        self.create_diameter_pressure_plot(diameter_df, base_plot_path)
                        
                    else:
                        print("Insufficient pressure data for interpolation")
                else:
                    print("Missing timestamp columns for synchronization")
            else:
                print("Pressure or timestamp data not available for synchronization")
                
        except Exception as e:
            print(f"Error in enhanced pressure analysis: {str(e)}")
            import traceback
            traceback.print_exc()

    def create_diameter_pressure_plot(self, combined_df, base_plot_path):
        """
        Buat plot gabungan diameter dan tekanan
        
        Args:
            combined_df (DataFrame): Data gabungan diameter dan tekanan
            base_plot_path (str): Base path untuk plot
        """
        try:
            # Create figure with dual y-axis
            fig, ax1 = plt.subplots(figsize=(15, 8))
            
            # Plot diameter
            color = 'tab:blue'
            ax1.set_xlabel('Frame Number')
            ax1.set_ylabel('Diameter (mm)', color=color)
            
            # Get diameter column name
            diameter_col = 'Diameter (mm)' if 'Diameter (mm)' in combined_df.columns else 'Diameter_mm'
            
            line1 = ax1.plot(combined_df['Frame'], combined_df[diameter_col], 
                           color=color, linewidth=1.5, label='Diameter', alpha=0.8)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(True, alpha=0.3)
            
            # Create second y-axis for pressure
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Pressure (arbitrary units)', color=color)
            line2 = ax2.plot(combined_df['Frame'], combined_df['pressure'], 
                           color=color, linewidth=1.5, label='Pressure', alpha=0.8)
            ax2.tick_params(axis='y', labelcolor=color)
            
            # Title and legend
            plt.title('Carotid Artery Diameter and Pressure Analysis', fontsize=14, fontweight='bold')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
            
            # Statistics
            avg_diameter = combined_df[diameter_col].mean()
            std_diameter = combined_df[diameter_col].std()
            avg_pressure = combined_df['pressure'].mean()
            std_pressure = combined_df['pressure'].std()
            
            stats_text = f'''Statistics:
Diameter: {avg_diameter:.2f} ± {std_diameter:.2f} mm
Pressure: {avg_pressure:.3f} ± {std_pressure:.3f} units
Correlation: {combined_df[diameter_col].corr(combined_df['pressure']):.3f}'''
            
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            # Save plot
            enhanced_plot_path = base_plot_path.replace('.png', '_with_pressure.png')
            plt.savefig(enhanced_plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Enhanced plot with pressure saved: {enhanced_plot_path}")
            
            # Create correlation analysis
            self.create_correlation_analysis(combined_df, diameter_col, base_plot_path)
            
        except Exception as e:
            print(f"Error creating diameter-pressure plot: {str(e)}")

    def create_correlation_analysis(self, combined_df, diameter_col, base_plot_path):
        """
        Buat analisis korelasi diameter-tekanan
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Scatter plot
            ax1.scatter(combined_df['pressure'], combined_df[diameter_col], 
                       alpha=0.6, c='purple', s=20)
            ax1.set_xlabel('Pressure (arbitrary units)')
            ax1.set_ylabel('Diameter (mm)')
            ax1.set_title('Diameter vs Pressure Correlation')
            ax1.grid(True, alpha=0.3)
            
            # Add correlation line
            z = np.polyfit(combined_df['pressure'], combined_df[diameter_col], 1)
            p = np.poly1d(z)
            ax1.plot(combined_df['pressure'], p(combined_df['pressure']), "r--", alpha=0.8)
            
            # Cross-correlation analysis
            from scipy.signal import correlate
            diameter_normalized = (combined_df[diameter_col] - combined_df[diameter_col].mean()) / combined_df[diameter_col].std()
            pressure_normalized = (combined_df['pressure'] - combined_df['pressure'].mean()) / combined_df['pressure'].std()
            
            correlation = correlate(diameter_normalized, pressure_normalized, mode='full')
            lags = np.arange(-len(pressure_normalized) + 1, len(diameter_normalized))
            
            ax2.plot(lags[:len(correlation)//2], correlation[:len(correlation)//2])
            ax2.set_xlabel('Lag (frames)')
            ax2.set_ylabel('Cross-correlation')
            ax2.set_title('Cross-correlation Analysis')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save correlation analysis
            correlation_plot_path = base_plot_path.replace('.png', '_correlation_analysis.png')
            plt.savefig(correlation_plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Correlation analysis saved: {correlation_plot_path}")
            
        except Exception as e:
            print(f"Error creating correlation analysis: {str(e)}")

def process_all_subjects():
    """
    Proses semua subjek dalam dataset
    """
    model_path = "UNet_25Mei_Sore.pth"
    processor = VideoProcessor(model_path)
    
    base_path = r"D:\Ridho\TA\fix banget\Dataset"
    
    # Process each subject
    for subject_num in range(1, 8):
        subject_folder = f"Subjek{subject_num}"
        video_path = os.path.join(base_path, subject_folder, f"Subjek{subject_num}.mp4")
        
        if os.path.exists(video_path):
            output_path = f"subjek{subject_num}_hasil_segmentasi_video_diameter.mp4"
            plot_path = f"subjek{subject_num}_diameter_vs_frame.png"
            csv_path = f"subjek{subject_num}_diameter_data.csv"
            
            print(f"\n=== Processing Subject {subject_num} ===")
            try:
                processor.process_video_with_diameter(
                    video_path=video_path,
                    output_path=output_path,
                    plot_path=plot_path,
                    csv_path=csv_path
                )
                print(f"Subject {subject_num} completed successfully!")
            except Exception as e:
                print(f"Error processing Subject {subject_num}: {str(e)}")
        else:
            print(f"Video file not found for Subject {subject_num}: {video_path}")

def process_selected_subject(subject_name):
    """
    Process video inference untuk subjek tertentu
    
    Args:
        subject_name (str): Nama subjek (misal: "Subjek1")
    
    Returns:
        dict: Status dan path hasil processing
    """
    model_path = "UNet_25Mei_Sore.pth"
    
    # Check if model exists
    if not os.path.exists(model_path):
        return {
            "status": "error",
            "message": f"Model file not found: {model_path}",
            "output_paths": {}
        }
    
    try:
        processor = VideoProcessor(model_path)
        
        # Create output directory
        output_dir = "inference_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        # Check if subject video exists
        video_path = f"data_uji\\{subject_name}\\{subject_name}.mp4"
        if not os.path.exists(video_path):
            return {
                "status": "error", 
                "message": f"Video file not found: {video_path}",
                "output_paths": {}
            }
        # Create subject-specific output directory
        subject_output_dir = os.path.join(output_dir, subject_name)
        if not os.path.exists(subject_output_dir):
            os.makedirs(subject_output_dir)
        
        output_path = os.path.join(subject_output_dir, f"{subject_name}_segmented_video.mp4")
        plot_path = os.path.join(subject_output_dir, f"{subject_name}_diameter_plot.png")
        csv_path = os.path.join(subject_output_dir, f"{subject_name}_diameter_data.csv")
        
        print(f"Processing {subject_name}...")
        processor.process_video_with_diameter(
            video_path=video_path,
            output_path=output_path,
            plot_path=plot_path,
            csv_path=csv_path
        )
        
        return {
            "status": "success",
            "message": f"Processing completed for {subject_name}",
            "output_paths": {
                "video": output_path,
                "plot": plot_path,
                "csv": csv_path,
                "directory": subject_output_dir
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing {subject_name}: {str(e)}",
            "output_paths": {}
        }

def get_available_subjects():
    """
    Dapatkan daftar subjek yang tersedia di data_uji
    
    Returns:
        list: Daftar nama subjek yang tersedia
    """
    subjects = []
    if os.path.exists("data_uji"):
        for item in os.listdir("data_uji"):
            subject_path = os.path.join("data_uji", item)
            if os.path.isdir(subject_path):
                # Check if video file exists
                video_file = os.path.join(subject_path, f"{item}.mp4")
                if os.path.exists(video_file):
                    subjects.append(item)
    return sorted(subjects)

def get_processed_results():
    """
    Dapatkan daftar hasil processing yang tersedia
    
    Returns:
        dict: Informasi hasil processing per subjek
    """
    results = {}
    output_dir = "inference_results"
    
    if os.path.exists(output_dir):
        for subject in os.listdir(output_dir):
            subject_path = os.path.join(output_dir, subject)
            if os.path.isdir(subject_path):
                results[subject] = {
                    "directory": subject_path,
                    "files": []
                }
                
                for file in os.listdir(subject_path):
                    file_path = os.path.join(subject_path, file)
                    if os.path.isfile(file_path):
                        results[subject]["files"].append({
                            "name": file,
                            "path": file_path,
                            "type": file.split('.')[-1] if '.' in file else "unknown"
                        })
    
    return results

def main():
    """
    Main function untuk menjalankan video inference
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Video Inference for Carotid Segmentation')
    parser.add_argument('--use_pressure', action='store_true', 
                       help='Use enhanced processing with pressure integration when available')
    parser.add_argument('--subject', type=str, default='Subjek1',
                       help='Subject name to process (default: Subjek1)')
    args = parser.parse_args()
    
    # Example usage - process one subject
    model_path = "UNet_25Mei_Sore.pth"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Please ensure you have trained the model using training_model.py first.")
        return
    
    processor = VideoProcessor(model_path)
    
    # Create output directory
    output_dir = "inference_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Process specified subject
    subject_name = args.subject
    video_path = f"data_uji\\{subject_name}\\{subject_name}.mp4"
    
    # Create subject-specific output directory
    subject_output_dir = os.path.join(output_dir, subject_name)
    if not os.path.exists(subject_output_dir):
        os.makedirs(subject_output_dir)
    
    output_path = os.path.join(subject_output_dir, f"{subject_name}_segmented_video.mp4")
    plot_path = os.path.join(subject_output_dir, f"{subject_name}_diameter_plot.png")
    csv_path = os.path.join(subject_output_dir, f"{subject_name}_diameter_data.csv")
    
    if os.path.exists(video_path):
        print(f"Processing {subject_name}...")
        
        # Check for pressure and timestamp files
        pressure_csv_path = f"data_uji\\{subject_name}\\subject{subject_name[-1]}.csv"
        timestamps_csv_path = f"data_uji\\{subject_name}\\timestamps.csv"
        
        # Use enhanced processing with pressure integration if requested and available
        if args.use_pressure and os.path.exists(pressure_csv_path) and os.path.exists(timestamps_csv_path):
            print("Found pressure and timestamp data - using enhanced processing...")
            processor.process_video_with_pressure_integration(
                video_path=video_path,
                output_path=output_path,
                plot_path=plot_path,
                csv_path=csv_path,
                pressure_csv_path=pressure_csv_path,
                timestamps_csv_path=timestamps_csv_path
            )
        else:
            if args.use_pressure:
                print("Enhanced processing requested but pressure/timestamp data not found - using standard processing...")
            else:
                print("Using standard processing...")
            processor.process_video_with_diameter(
                video_path=video_path,
                output_path=output_path,
                plot_path=plot_path,
                csv_path=csv_path
            )
            
        print(f"[SUCCESS] Processing completed!")
        print(f"Output video: {output_path}")
        print(f"Plot saved: {plot_path}")
        print(f"CSV data: {csv_path}")
        
        # Check for enhanced outputs
        enhanced_csv = csv_path.replace('.csv', '_with_pressure.csv')
        enhanced_plot = plot_path.replace('.png', '_with_pressure.png')
        correlation_plot = plot_path.replace('.png', '_correlation_analysis.png');
        
        if os.path.exists(enhanced_csv):
            print(f"Enhanced CSV with pressure: {enhanced_csv}")
        if os.path.exists(enhanced_plot):
            print(f"Enhanced plot with pressure: {enhanced_plot}")
        if os.path.exists(correlation_plot):
            print(f"Correlation analysis: {correlation_plot}")
    else:
        print(f"Video file not found: {video_path}")
        print("Available subjects in data_uji:")
        if os.path.exists("data_uji"):
            subjects = [d for d in os.listdir("data_uji") if os.path.isdir(os.path.join("data_uji", d))]
            for subj in subjects:
                subj_path = os.path.join("data_uji", subj)
                videos = [f for f in os.listdir(subj_path) if f.endswith('.mp4')]
                print(f"  - {subj}: {videos}")
        else:
            print("  data_uji directory not found!")
            
    print("\\nTo process all subjects, uncomment the process_all_subjects() call.")
    
    # Uncomment to process all subjects
    # process_all_subjects()

if __name__ == "__main__":
    main()

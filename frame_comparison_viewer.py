import os
import cv2
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PIL import Image, ImageTk
import glob
from theme_manager import ThemeManager

class FrameComparisonViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Frame Comparison Viewer - Dual Frame Analysis with Vertical Lines")
        self.root.geometry("1600x1000")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Data containers
        self.video_path = None
        self.segmented_video_path = None
        self.diameter_data = None
        self.pressure_data = None
        self.synced_data = None
        self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        
        # Frame comparison specific variables
        self.frame1_index = 0
        self.frame2_index = 0
        self.vertical_line1 = None
        self.vertical_line2 = None
        
        # Available subjects
        self.available_subjects = []
        self.detect_available_subjects()
        
        self.setup_ui()
        self.setup_menu_with_theme()
        
        # Apply initial theme
        self.apply_current_theme()
    
    def detect_available_subjects(self):
        """Detect available subjects from data_uji folder"""
        self.available_subjects = []
        
        try:
            data_uji_path = "data_uji"
            if os.path.exists(data_uji_path):
                # Look for subject folders
                for item in sorted(os.listdir(data_uji_path)):
                    subject_path = os.path.join(data_uji_path, item)
                    if os.path.isdir(subject_path):
                        # Check if folder contains video files
                        video_files = glob.glob(os.path.join(subject_path, "*.mp4"))
                        if video_files:
                            # Check for inference results
                            inference_path = os.path.join("inference_results", item)
                            has_inference = os.path.exists(inference_path)
                            
                            if has_inference:
                                # Check for diameter data
                                diameter_files = glob.glob(os.path.join(inference_path, "*diameter_data*.csv"))
                                status = "✅ Complete" if diameter_files else "⚠️ No Analysis"
                            else:
                                status = "❌ No Results"
                            
                            self.available_subjects.append(f"{item} [{status}]")
                        
            if not self.available_subjects:
                self.available_subjects = ["No subjects found"]
                
        except Exception as e:
            print(f"Error detecting subjects: {e}")
            self.available_subjects = ["Error detecting subjects"]
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subject selection dropdown
        ttk.Label(control_frame, text="Subject:").pack(side=tk.LEFT, padx=(0, 5))
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(control_frame, textvariable=self.subject_var, 
                                        values=self.available_subjects, width=25, state="readonly")
        self.subject_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.subject_combo.bind('<<ComboboxSelected>>', self.on_subject_change)
        
        # Set default selection if subjects are available
        if self.available_subjects and not self.available_subjects[0].startswith("No"):
            self.subject_combo.set(self.available_subjects[0])
        
        # Load subject button
        ttk.Button(control_frame, text="Load Selected", command=self.load_selected_subject).pack(side=tk.LEFT, padx=(0, 10))
        
        # Browse button
        ttk.Button(control_frame, text="Browse...", command=self.load_subject).pack(side=tk.LEFT, padx=(0, 20))
        
        # Frame comparison controls
        frame_control_frame = ttk.LabelFrame(main_frame, text="Frame Comparison Controls", padding=10)
        frame_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame 1 control
        frame1_frame = ttk.Frame(frame_control_frame)
        frame1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(frame1_frame, text="Frame 1:", foreground="blue").pack(side=tk.LEFT, padx=(0, 5))
        self.frame1_var = tk.IntVar()
        self.frame1_scale = ttk.Scale(frame1_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     variable=self.frame1_var, command=self.on_frame1_change, length=300)
        self.frame1_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frame1_label = ttk.Label(frame1_frame, text="0/0")
        self.frame1_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame 1 info
        self.frame1_info_label = ttk.Label(frame1_frame, text="Diameter: -- | Pressure: -- N", foreground="blue")
        self.frame1_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame 2 control
        frame2_frame = ttk.Frame(frame_control_frame)
        frame2_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(frame2_frame, text="Frame 2:", foreground="red").pack(side=tk.LEFT, padx=(0, 5))
        self.frame2_var = tk.IntVar()
        self.frame2_scale = ttk.Scale(frame2_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     variable=self.frame2_var, command=self.on_frame2_change, length=300)
        self.frame2_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frame2_label = ttk.Label(frame2_frame, text="0/0")
        self.frame2_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame 2 info
        self.frame2_info_label = ttk.Label(frame2_frame, text="Diameter: -- | Pressure: -- N", foreground="red")
        self.frame2_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Content frame (split between images and plot)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Video frames display
        video_frame = ttk.LabelFrame(content_frame, text="Frame Comparison Display", padding=10)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame images container
        frames_container = ttk.Frame(video_frame)
        frames_container.pack(expand=True, fill=tk.BOTH)
        
        # Frame 1 display
        frame1_container = ttk.LabelFrame(frames_container, text="Frame 1 (Blue Line)", padding=5)
        frame1_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.video1_label = ttk.Label(frame1_container, text="Select a subject and click 'Load Selected'")
        self.video1_label.pack(expand=True)
        
        # Frame 2 display
        frame2_container = ttk.LabelFrame(frames_container, text="Frame 2 (Red Line)", padding=5)
        frame2_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.video2_label = ttk.Label(frame2_container, text="Select a subject and click 'Load Selected'")
        self.video2_label.pack(expand=True)
        
        # Right side - Plot with vertical lines
        plot_frame = ttk.LabelFrame(content_frame, text="Diameter vs Pressure Analysis with Frame Indicators", padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect mouse click event for interactive frame selection
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        self.status_var.set(f"Ready - {len(self.available_subjects)} subjects detected")
        
        # Initialize plot
        self.update_plot()
    
    def setup_menu_with_theme(self):
        """Setup menu bar with theme options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        theme_menu.add_separator()
        theme_menu.add_command(label="Reset to Default", command=lambda: self.change_theme("default"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Usage Instructions", command=self.show_instructions)
    
    def change_theme(self, theme_name):
        """Change application theme"""
        try:
            self.theme_manager.set_theme(theme_name)
            self.apply_current_theme()
            self.status_var.set(f"Theme changed to: {theme_name}")
        except Exception as e:
            messagebox.showerror("Theme Error", f"Failed to change theme: {str(e)}")
    
    def apply_current_theme(self):
        """Apply current theme to the application"""
        try:
            theme = self.theme_manager.get_current_theme()
            
            # Apply to root window
            self.root.configure(bg=theme.get('bg', 'white'))
            
            # Update matplotlib figure colors
            if hasattr(self, 'fig') and hasattr(self, 'ax'):
                self.fig.patch.set_facecolor(theme.get('plot_bg', 'white'))
                self.ax.set_facecolor(theme.get('plot_bg', 'white'))
                self.canvas.draw()
                
        except Exception as e:
            print(f"Theme application error: {e}")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                          "Frame Comparison Viewer v1.0\n\n"
                          "Advanced frame-by-frame comparison tool\n"
                          "with dual vertical line indicators for\n"
                          "diameter and pressure analysis.\n\n"
                          "Features:\n"
                          "• Dual frame display\n"
                          "• Interactive plot selection\n"
                          "• Real-time data comparison\n"
                          "• Vertical line indicators")
    
    def show_instructions(self):
        """Show usage instructions"""
        instructions = """Frame Comparison Viewer - Usage Instructions

1. LOADING DATA:
   • Select a subject from the dropdown
   • Click 'Load Selected' to load data
   • Or use 'Browse...' to select custom folder

2. FRAME COMPARISON:
   • Use Frame 1 slider (Blue) to select first frame
   • Use Frame 2 slider (Red) to select second frame
   • Both frames will be displayed side by side

3. INTERACTIVE PLOT:
   • Blue vertical line shows Frame 1 position
   • Red vertical line shows Frame 2 position
   • Click on plot to quickly set frame positions
   • Left click sets Frame 1, Right click sets Frame 2

4. DATA DISPLAY:
   • Frame details show Diameter and Pressure values
   • Color-coded for easy identification
   • Real-time updates as you move sliders

5. THEMES:
   • Use Theme menu to switch between light/dark modes
   • Themes affect both UI and plot appearance"""
        
        messagebox.showinfo("Usage Instructions", instructions)
    
    def on_subject_change(self, event=None):
        """Handle subject selection change"""
        selected = self.subject_var.get()
        if selected and not selected.startswith("No subjects") and not selected.startswith("Error"):
            # Extract subject name (remove status part)
            subject_name = selected.split(" [")[0]
            self.status_var.set(f"Selected: {subject_name} - Click 'Load Selected' to begin")
    
    def load_selected_subject(self):
        """Load the selected subject from dropdown"""
        selected = self.subject_var.get()
        if not selected or selected.startswith("No subjects") or selected.startswith("Error"):
            messagebox.showwarning("Warning", "Please select a valid subject first")
            return
            
        # Extract subject name (remove status part)
        subject_name = selected.split(" [")[0]
        subject_path = os.path.join("data_uji", subject_name)
        
        if not os.path.exists(subject_path):
            messagebox.showerror("Error", f"Subject folder not found: {subject_path}")
            return
            
        self.load_subject_from_path(subject_path)
        
    def load_subject(self):
        """Load subject data via folder browser"""
        folder = filedialog.askdirectory(title="Select Subject Folder")
        if not folder:
            return
        self.load_subject_from_path(folder)
            
    def load_subject_from_path(self, folder):
        """Load subject data from specified path"""
        try:
            subject_name = os.path.basename(folder)
            self.status_var.set(f"Loading {subject_name}...")
            
            # Find video files
            video_files = glob.glob(os.path.join(folder, "*.mp4"))
            if not video_files:
                messagebox.showerror("Error", "No video files found in selected folder")
                return
                
            # Check for segmented video in inference_results
            inference_folder = os.path.join("inference_results", subject_name)
            segmented_video = None
            
            if os.path.exists(inference_folder):
                segmented_files = glob.glob(os.path.join(inference_folder, "*segmented_video*.mp4"))
                if segmented_files:
                    segmented_video = segmented_files[0]
            
            # Prioritize segmented video if available
            if segmented_video and os.path.exists(segmented_video):
                self.segmented_video_path = segmented_video
                self.video_path = segmented_video
                self.status_var.set(f"Using segmented video: {os.path.basename(segmented_video)}")
                print(f"DEBUG: Loading segmented video: {segmented_video}")
            else:
                self.video_path = video_files[0]
                self.segmented_video_path = None
                self.status_var.set(f"Using original video: {os.path.basename(self.video_path)}")
                print(f"DEBUG: Loading original video: {self.video_path}")
            
            # Load video
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if self.total_frames == 0:
                messagebox.showerror("Error", "Could not load video file")
                return
                
            print(f"DEBUG: Video loaded - {self.total_frames} frames")
            
            # Update frame scales
            self.frame1_scale.configure(to=self.total_frames-1)
            self.frame2_scale.configure(to=self.total_frames-1)
            
            # Set initial frame positions
            self.frame1_var.set(0)
            self.frame2_var.set(min(self.total_frames-1, self.total_frames//2))
            self.frame1_index = 0
            self.frame2_index = min(self.total_frames-1, self.total_frames//2)
            
            # Load diameter data
            self.load_diameter_data(subject_name)
            
            # Load pressure data  
            self.load_pressure_data(folder)
            
            # Sync data
            self.sync_data()
            
            # Display frames and update plot
            self.display_frames()
            self.update_plot()
            self.update_frame_info()
            
            # Final status message
            data_status = []
            if self.diameter_data is not None:
                data_status.append("Diameter ✅")
            if self.pressure_data is not None:
                data_status.append("Pressure ✅")
            
            status_msg = f"Loaded {subject_name} - {self.total_frames} frames"
            if data_status:
                status_msg += f" | Data: {', '.join(data_status)}"
            else:
                status_msg += " | Video only"
            self.status_var.set(status_msg)
            
            print(f"DEBUG: Load complete - {status_msg}")
            
        except Exception as e:
            error_msg = f"Failed to load subject: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error loading subject")
            print(f"DEBUG: Error - {error_msg}")
    
    def load_diameter_data(self, subject_name):
        """Load diameter data from CSV files"""
        # Look for diameter data in inference_results folder
        inference_folder = os.path.join("inference_results", subject_name)
        
        diameter_files = []
        if os.path.exists(inference_folder):
            diameter_files = glob.glob(os.path.join(inference_folder, "*diameter_data*.csv"))
        
        if diameter_files:
            # Prioritize files with pressure data
            pressure_files = [f for f in diameter_files if 'pressure' in f.lower()]
            if pressure_files:
                self.diameter_data = pd.read_csv(pressure_files[0])
                print(f"DEBUG: Loaded diameter data with pressure: {len(self.diameter_data)} rows")
            else:
                self.diameter_data = pd.read_csv(diameter_files[0])
                print(f"DEBUG: Loaded diameter data: {len(self.diameter_data)} rows")
            
            print(f"DEBUG: Diameter columns: {list(self.diameter_data.columns)}")
              # Check for different diameter column names and standardize
            diameter_col = None
            possible_diameter_cols = [
                'diameter', 'Diameter', 'avg_diameter', 'mean_diameter', 
                'diameter_pixels', 'Diameter (mm)', 'Diameter (pixels)',
                'diameter_mm', 'avg_diameter_mm'
            ]
            
            for col in possible_diameter_cols:
                if col in self.diameter_data.columns:
                    diameter_col = col
                    break
            
            if diameter_col:
                if diameter_col != 'diameter':
                    self.diameter_data['diameter'] = self.diameter_data[diameter_col]
                    print(f"DEBUG: Standardized diameter column from '{diameter_col}' to 'diameter'")
                
                # Ensure numeric data
                self.diameter_data['diameter'] = pd.to_numeric(self.diameter_data['diameter'], errors='coerce')
                valid_count = self.diameter_data['diameter'].notna().sum()
                print(f"DEBUG: {valid_count} valid diameter measurements")
            else:
                print(f"DEBUG: No diameter column found in: {list(self.diameter_data.columns)}")
            
        else:
            self.diameter_data = None
            print("DEBUG: No diameter data found")
            
    def load_pressure_data(self, folder):
        """Load pressure data from CSV files"""
        # Look for pressure data in the subject folder
        csv_files = glob.glob(os.path.join(folder, "*.csv"))
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Check if this file contains pressure data
                if 'pressure' in df.columns or 'Pressure' in df.columns:
                    self.pressure_data = df
                    print(f"DEBUG: Loaded pressure data: {len(self.pressure_data)} rows")
                    print(f"DEBUG: Pressure columns: {list(self.pressure_data.columns)}")
                    break
            except Exception as e:
                print(f"DEBUG: Error reading {csv_file}: {e}")
                continue
        
        if self.pressure_data is None:            print("DEBUG: No pressure data found")
    
    def sync_data(self):
        """Synchronize diameter and pressure data"""
        if self.diameter_data is None:
            self.synced_data = None
            print("DEBUG: No diameter data to sync")
            return
            
        # Create frame-based data
        self.synced_data = self.diameter_data.copy()
        print(f"DEBUG: Starting sync with {len(self.synced_data)} diameter records")
          # Ensure frame column exists and is properly indexed
        if 'frame' not in self.synced_data.columns:
            if 'Frame' in self.synced_data.columns:
                self.synced_data['frame'] = self.synced_data['Frame']
                print("DEBUG: Used 'Frame' column as frame index")
            elif 'frame_number' in self.synced_data.columns:
                self.synced_data['frame'] = self.synced_data['frame_number']
                print("DEBUG: Used 'frame_number' column as frame index")
            else:
                # Create frame index based on row position
                self.synced_data['frame'] = range(len(self.synced_data))
                print("DEBUG: Created frame index from row positions")
        
        # Ensure frame column is numeric
        self.synced_data['frame'] = pd.to_numeric(self.synced_data['frame'], errors='coerce')
        self.synced_data = self.synced_data.dropna(subset=['frame'])
        
        # Keep original frame numbers but create normalized frames for video indexing
        self.synced_data['original_frame'] = self.synced_data['frame'].copy()
        
        # Adjust frame indexing to match video frames (0-based)
        min_frame = self.synced_data['frame'].min()
        max_frame = self.synced_data['frame'].max()
        print(f"DEBUG: Original frame range: {min_frame:.0f} to {max_frame:.0f}")
          # Check if we need to adjust frame indexing to match video
        if hasattr(self, 'total_frames') and self.total_frames > 0:
            print(f"DEBUG: Video has {self.total_frames} frames")
            
            if min_frame >= self.total_frames:
                # Frames are way beyond video length, map to video range
                frame_range = max_frame - min_frame + 1
                if frame_range <= self.total_frames:
                    # Simple offset mapping
                    self.synced_data['frame'] = self.synced_data['frame'] - min_frame
                    print(f"DEBUG: Mapped frames to 0-{frame_range-1} to match video")
                else:
                    # Scale frames to fit video
                    scale_factor = (self.total_frames - 1) / (max_frame - min_frame)
                    self.synced_data['frame'] = (self.synced_data['frame'] - min_frame) * scale_factor
                    self.synced_data['frame'] = self.synced_data['frame'].round().astype(int)
                    print(f"DEBUG: Scaled frames to fit video (scale factor: {scale_factor:.3f})")
                    
            elif max_frame >= self.total_frames:
                # Some frames exceed video length, scale to fit
                scale_factor = (self.total_frames - 1) / (max_frame - min_frame)
                self.synced_data['frame'] = (self.synced_data['frame'] - min_frame) * scale_factor
                self.synced_data['frame'] = self.synced_data['frame'].round().astype(int)
                print(f"DEBUG: Scaled frames to fit video length (scale factor: {scale_factor:.3f})")
                
            elif min_frame > 0:
                # Frames start from a positive number but within video range
                # Keep original frame numbers if they fit, otherwise offset
                if max_frame < self.total_frames:
                    print(f"DEBUG: Keeping original frame numbers (within video range)")
                else:
                    self.synced_data['frame'] = self.synced_data['frame'] - min_frame
                    print(f"DEBUG: Offset frames to start from 0")
        else:
            print("DEBUG: No video loaded yet, keeping original frame numbers")
        
        print(f"DEBUG: Final frame range: {self.synced_data['frame'].min():.0f} to {self.synced_data['frame'].max():.0f}")
        
        # Add pressure data if available
        if self.pressure_data is not None:
            print(f"DEBUG: Adding pressure data ({len(self.pressure_data)} records)")
            # Try to merge pressure data
            if 'pressure' not in self.synced_data.columns and 'Pressure' not in self.synced_data.columns:
                # Simple approach: assume same length and merge by index
                if len(self.pressure_data) >= len(self.synced_data):
                    pressure_col = 'pressure' if 'pressure' in self.pressure_data.columns else 'Pressure'
                    if pressure_col in self.pressure_data.columns:
                        self.synced_data['pressure'] = self.pressure_data[pressure_col][:len(self.synced_data)]
                        print(f"DEBUG: Added pressure data from column '{pressure_col}'")
        
        # Final data validation
        self.synced_data = self.synced_data.sort_values('frame').reset_index(drop=True)
        
        print(f"DEBUG: Synced data complete - {len(self.synced_data)} rows")
        print(f"DEBUG: Synced columns: {list(self.synced_data.columns)}")
        print(f"DEBUG: Frame range: {self.synced_data['frame'].min():.0f} to {self.synced_data['frame'].max():.0f}")
        
        # Show sample data
        if len(self.synced_data) > 0:
            sample = self.synced_data.head(3)
            print("DEBUG: Sample synced data:")
            for idx, row in sample.iterrows():
                frame_val = row.get('frame', 'N/A')
                diameter_val = row.get('diameter', 'N/A')
                pressure_val = row.get('pressure', 'N/A')
                print(f"  Frame {frame_val}: Diameter={diameter_val}, Pressure={pressure_val}")
    
    def on_frame1_change(self, event):
        """Handle frame 1 slider change"""
        self.frame1_index = int(self.frame1_var.get())
        self.display_frames()
        self.update_plot()
        self.update_frame_info()
    
    def on_frame2_change(self, event):
        """Handle frame 2 slider change"""
        self.frame2_index = int(self.frame2_var.get())
        self.display_frames()
        self.update_plot()
        self.update_frame_info()
    
    def on_plot_click(self, event):
        """Handle plot click for interactive frame selection"""
        if event.inaxes != self.ax or self.synced_data is None:
            return
            
        # Get clicked x-coordinate (frame)
        clicked_frame = int(event.xdata)
        
        # Clamp to valid range
        clicked_frame = max(0, min(clicked_frame, self.total_frames - 1))
        
        # Left click sets Frame 1, Right click sets Frame 2
        if event.button == 1:  # Left click
            self.frame1_var.set(clicked_frame)
            self.frame1_index = clicked_frame
        elif event.button == 3:  # Right click
            self.frame2_var.set(clicked_frame)
            self.frame2_index = clicked_frame
        
        self.display_frames()
        self.update_plot()
        self.update_frame_info()
    
    def display_frames(self):
        """Display both selected frames"""
        if not self.cap or self.total_frames == 0:
            return
            
        try:
            # Display Frame 1
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame1_index)
            ret1, frame1 = self.cap.read()
            
            if ret1:
                # Convert BGR to RGB
                frame1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)                # Resize for display (larger size)
                height, width = frame1_rgb.shape[:2]
                max_height = 350  # Increased from 200 to 350
                if height > max_height:
                    scale = max_height / height
                    new_width = int(width * scale)
                    frame1_rgb = cv2.resize(frame1_rgb, (new_width, max_height))
                
                # Convert to PIL and then to Tkinter format
                frame1_pil = Image.fromarray(frame1_rgb)
                frame1_tk = ImageTk.PhotoImage(frame1_pil)
                
                # Update label
                self.video1_label.configure(image=frame1_tk, text="")
                self.video1_label.image = frame1_tk  # Keep a reference
            
            # Display Frame 2
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame2_index)
            ret2, frame2 = self.cap.read()
            
            if ret2:
                # Convert BGR to RGB
                frame2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)                # Resize for display (larger size)
                height, width = frame2_rgb.shape[:2]
                max_height = 350  # Increased from 200 to 350
                if height > max_height:
                    scale = max_height / height
                    new_width = int(width * scale)
                    frame2_rgb = cv2.resize(frame2_rgb, (new_width, max_height))
                
                # Convert to PIL and then to Tkinter format
                frame2_pil = Image.fromarray(frame2_rgb)
                frame2_tk = ImageTk.PhotoImage(frame2_pil)
                
                # Update label
                self.video2_label.configure(image=frame2_tk, text="")
                self.video2_label.image = frame2_tk  # Keep a reference            # Update frame labels
            self.frame1_label.configure(text=f"{self.frame1_index}/{self.total_frames-1}")
            self.frame2_label.configure(text=f"{self.frame2_index}/{self.total_frames-1}")
            
        except Exception as e:
            print(f"DEBUG: Error displaying frames: {e}")
    
    def update_frame_info(self):
        """Update frame information display"""
        if self.synced_data is None:
            self.frame1_info_label.configure(text="Diameter: -- | Pressure: -- N")
            self.frame2_info_label.configure(text="Diameter: -- | Pressure: -- N")
            return
        
        try:
            # Get data for Frame 1 - try exact match first, then closest
            frame1_data = self.synced_data[self.synced_data['frame'] == self.frame1_index]
            if frame1_data.empty:
                # Find closest frame
                closest_idx = (self.synced_data['frame'] - self.frame1_index).abs().idxmin()
                frame1_data = self.synced_data.loc[[closest_idx]]
                print(f"DEBUG: Using closest frame for Frame 1: {self.synced_data.loc[closest_idx, 'frame']}")
            
            if not frame1_data.empty:                # Try different diameter column names
                diameter1 = '--'
                for col in ['diameter', 'Diameter (mm)', 'Diameter', 'avg_diameter']:
                    if col in frame1_data.columns:
                        val = frame1_data.iloc[0].get(col, '--')
                        if val != '--' and pd.notna(val):
                            diameter1 = f"{float(val):.2f}"
                            break
                
                pressure1 = frame1_data.iloc[0].get('pressure', '--')
                if pressure1 != '--' and pd.notna(pressure1):
                    pressure1 = f"{float(pressure1):.2f} N"
                else:
                    pressure1 = "-- N"
                
                frame1_info = f"Diameter: {diameter1} | Pressure: {pressure1}"
            else:                frame1_info = "Diameter: -- | Pressure: -- N"
            
            # Get data for Frame 2 - try exact match first, then closest
            frame2_data = self.synced_data[self.synced_data['frame'] == self.frame2_index]
            if frame2_data.empty:
                # Find closest frame
                closest_idx = (self.synced_data['frame'] - self.frame2_index).abs().idxmin()
                frame2_data = self.synced_data.loc[[closest_idx]]
                print(f"DEBUG: Using closest frame for Frame 2: {self.synced_data.loc[closest_idx, 'frame']}")
            
            if not frame2_data.empty:
                # Try different diameter column names
                diameter2 = '--'
                for col in ['diameter', 'Diameter (mm)', 'Diameter', 'avg_diameter']:
                    if col in frame2_data.columns:
                        val = frame2_data.iloc[0].get(col, '--')
                        if val != '--' and pd.notna(val):
                            diameter2 = f"{float(val):.2f}"
                            break
                
                pressure2 = frame2_data.iloc[0].get('pressure', '--')
                if pressure2 != '--' and pd.notna(pressure2):
                    pressure2 = f"{float(pressure2):.2f} N"
                else:
                    pressure2 = "-- N"
                
                frame2_info = f"Diameter: {diameter2} | Pressure: {pressure2}"
            else:
                frame2_info = "Diameter: -- | Pressure: -- N"
            
            self.frame1_info_label.configure(text=frame1_info)
            self.frame2_info_label.configure(text=frame2_info)
            
        except Exception as e:
            print(f"DEBUG: Error updating frame info: {e}")
            self.frame1_info_label.configure(text="Diameter: -- | Pressure: -- N")
            self.frame2_info_label.configure(text="Diameter: -- | Pressure: -- N")
    
    def update_plot(self):
        """Update the plot with dual vertical lines"""
        self.ax.clear()
        
        if self.synced_data is None or self.synced_data.empty:
            self.ax.text(0.5, 0.5, 'No data available\nLoad a subject to view analysis', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        try:
            # Debug: Print available columns
            print(f"DEBUG: Available columns for plotting: {list(self.synced_data.columns)}")
              # Plot diameter data
            diameter_plotted = False
            if 'diameter' in self.synced_data.columns:
                diameter_values = pd.to_numeric(self.synced_data['diameter'], errors='coerce')
                valid_diameter = ~diameter_values.isna()
                
                print(f"DEBUG: Found {valid_diameter.sum()} valid diameter values out of {len(diameter_values)}")
                
                if valid_diameter.any():
                    frames = self.synced_data.loc[valid_diameter, 'frame']
                    diameters = diameter_values[valid_diameter]
                    
                    print(f"DEBUG: Plotting diameter - Frame range: {frames.min():.0f}-{frames.max():.0f}, Diameter range: {diameters.min():.2f}-{diameters.max():.2f}")
                    
                    self.ax.plot(frames, diameters, 'b-', linewidth=2, label='Diameter', alpha=0.8)
                    self.ax.set_ylabel('Diameter (mm)', color='b')  # Changed from pixels to mm
                    self.ax.tick_params(axis='y', labelcolor='b')
                    diameter_plotted = True
                else:
                    print("DEBUG: No valid diameter values found")
            else:
                print("DEBUG: No 'diameter' column found in synced_data")
                # Try to plot with original column name if standardization failed
                original_cols = [col for col in self.synced_data.columns if 'diameter' in col.lower() or 'Diameter' in col]
                if original_cols:
                    col_name = original_cols[0]
                    print(f"DEBUG: Attempting to plot with original column: {col_name}")
                    diameter_values = pd.to_numeric(self.synced_data[col_name], errors='coerce')
                    valid_diameter = ~diameter_values.isna()
                    
                    if valid_diameter.any():
                        frames = self.synced_data.loc[valid_diameter, 'frame']
                        diameters = diameter_values[valid_diameter]
                        
                        self.ax.plot(frames, diameters, 'b-', linewidth=2, label=f'Diameter ({col_name})', alpha=0.8)
                        self.ax.set_ylabel(f'{col_name}', color='b')
                        self.ax.tick_params(axis='y', labelcolor='b')
                        diameter_plotted = True
                        print(f"DEBUG: Successfully plotted with {col_name}")
                else:
                    print(f"DEBUG: Available columns: {list(self.synced_data.columns)}")
              # Plot pressure data on secondary y-axis if available
            pressure_plotted = False
            if 'pressure' in self.synced_data.columns:
                pressure_values = pd.to_numeric(self.synced_data['pressure'], errors='coerce')
                valid_pressure = ~pressure_values.isna()
                
                print(f"DEBUG: Found {valid_pressure.sum()} valid pressure values out of {len(pressure_values)}")
                
                if valid_pressure.any():
                    # Create secondary y-axis only if diameter was plotted
                    if diameter_plotted:
                        ax2 = self.ax.twinx()
                    else:
                        ax2 = self.ax
                    
                    frames = self.synced_data.loc[valid_pressure, 'frame']
                    pressures = pressure_values[valid_pressure]
                    
                    print(f"DEBUG: Plotting pressure - Frame range: {frames.min():.0f}-{frames.max():.0f}, Pressure range: {pressures.min():.2f}-{pressures.max():.2f}")
                    ax2.plot(frames, pressures, 'g--', linewidth=2, label='Pressure', alpha=0.8)
                    ax2.set_ylabel('Pressure (N)', color='g')  # Changed to Newton (N)
                    ax2.tick_params(axis='y', labelcolor='g')
                    pressure_plotted = True
            
            # If no data was plotted, show sample data or message
            if not diameter_plotted and not pressure_plotted:
                # Create sample data for visualization
                frames = self.synced_data['frame']
                self.ax.plot(frames, [50] * len(frames), 'r--', alpha=0.3, label='No data - sample line')
                self.ax.text(0.5, 0.5, 'No valid data to plot\nCheck data files and columns', 
                            horizontalalignment='center', verticalalignment='center', 
                            transform=self.ax.transAxes, fontsize=10, color='red')
            
            # Add vertical lines for selected frames
            if hasattr(self, 'frame1_index'):
                self.vertical_line1 = self.ax.axvline(x=self.frame1_index, color='blue', 
                                                     linestyle='-', linewidth=3, alpha=0.8, 
                                                     label=f'Frame 1 ({self.frame1_index})')
            
            if hasattr(self, 'frame2_index'):
                self.vertical_line2 = self.ax.axvline(x=self.frame2_index, color='red', 
                                                     linestyle='-', linewidth=3, alpha=0.8, 
                                                     label=f'Frame 2 ({self.frame2_index})')
            
            # Set labels and title
            self.ax.set_xlabel('Frame Number')
            self.ax.set_title('Diameter vs Pressure Analysis with Frame Comparison')
            self.ax.grid(True, alpha=0.3)
            
            # Add legend - collect all handles and labels
            lines1, labels1 = self.ax.get_legend_handles_labels()
            lines, labels = lines1, labels1
            
            # Add pressure legend if it exists on secondary axis
            if pressure_plotted and diameter_plotted and 'ax2' in locals():
                lines2, labels2 = ax2.get_legend_handles_labels()
                lines += lines2
                labels += labels2
            
            if lines:
                self.ax.legend(lines, labels, loc='upper right')            # Set axis limits - Always start from 0 and show all data
            if not self.synced_data.empty:
                frame_min = 0  # Always start from 0
                frame_max = self.synced_data['frame'].max()
                
                # Ensure we show the full range with some padding
                total_range = frame_max - frame_min
                padding = max(5, total_range * 0.02)  # 2% padding or minimum 5 frames
                
                self.ax.set_xlim(frame_min, frame_max + padding)
                
                # Set y-axis limits for better visualization
                if diameter_plotted:
                    diameter_values = pd.to_numeric(self.synced_data['diameter'], errors='coerce')
                    valid_diameters = diameter_values.dropna()
                    if len(valid_diameters) > 0:
                        y_min = valid_diameters.min() * 0.95
                        y_max = valid_diameters.max() * 1.05
                        self.ax.set_ylim(y_min, y_max)
            
        except Exception as e:
            print(f"DEBUG: Error updating plot: {e}")
            import traceback
            traceback.print_exc()
            self.ax.text(0.5, 0.5, f'Error updating plot:\n{str(e)[:100]}', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=10, color='red')
        
        # Apply current theme to plot
        self.apply_current_theme()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = FrameComparisonViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

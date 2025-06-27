import os
import cv2
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
import glob
from theme_manager import ThemeManager

class EnhancedDataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Data Viewer - Overlay & Diameter Analysis")
        self.root.geometry("1400x900")
        
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
                                status = "[SUCCESS] Complete" if diameter_files else "[WARN] No Analysis"
                            else:
                                status = "[ERROR] No Results"
                            
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
        
        # Load subject button (now loads selected subject)
        ttk.Button(control_frame, text="Load Selected", command=self.load_selected_subject).pack(side=tk.LEFT, padx=(0, 10))
        
        # Browse button (for custom folder selection)
        ttk.Button(control_frame, text="Browse...", command=self.load_subject).pack(side=tk.LEFT, padx=(0, 20))
        
        # Frame control
        ttk.Label(control_frame, text="Frame:").pack(side=tk.LEFT, padx=(20, 5))
        self.frame_var = tk.IntVar()
        self.frame_scale = ttk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                   variable=self.frame_var, command=self.on_frame_change, length=300)
        self.frame_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frame_label = ttk.Label(control_frame, text="0/0")
        self.frame_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Play/Pause buttons
        ttk.Button(control_frame, text="Play", command=self.play_video).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Pause", command=self.pause_video).pack(side=tk.LEFT)
        
        # Content frame (split between image and plot)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Video display
        video_frame = ttk.LabelFrame(content_frame, text="Video Display (Overlay Priority)", padding=10)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = ttk.Label(video_frame, text="Select a subject and click 'Load Selected'")
        self.video_label.pack(expand=True)
        
        # Right side - Plot
        plot_frame = ttk.LabelFrame(content_frame, text="Diameter vs Pressure Analysis", padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        self.status_var.set(f"Ready - {len(self.available_subjects)} subjects detected")
        
        # Auto-play variables
        self.is_playing = False
        self.play_job = None
        
        # Initialize plot
        self.update_plot()
    
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
            
            # Update frame scale
            self.frame_scale.configure(to=self.total_frames-1)
            self.frame_var.set(0)
            self.current_frame = 0
            
            # Load diameter data
            self.load_diameter_data(subject_name)
            
            # Load pressure data  
            self.load_pressure_data(folder)
            
            # Sync data
            self.sync_data()
            
            # Display first frame and update plot
            self.display_frame()
            self.update_plot()
            
            # Final status message
            data_status = []
            if self.diameter_data is not None:
                data_status.append("Diameter [SUCCESS]")
            if self.pressure_data is not None:
                data_status.append("Pressure [SUCCESS]")
            
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
                if any('pressure' in col.lower() or 'sensor' in col.lower() for col in df.columns):
                    self.pressure_data = df
                    print(f"DEBUG: Loaded pressure data: {len(df)} rows")
                    print(f"DEBUG: Pressure columns: {list(df.columns)}")
                    break
            except Exception as e:
                print(f"DEBUG: Error reading {csv_file}: {e}")
                continue
        else:
            self.pressure_data = None
            print("DEBUG: No pressure data found")
            
    def sync_data(self):
        """Synchronize diameter and pressure data"""
        try:
            # Create basic synchronized dataframe with video frames
            self.synced_data = pd.DataFrame()
            self.synced_data['Frame'] = range(self.total_frames)
            
            # Try to add diameter data
            if self.diameter_data is not None and not self.diameter_data.empty:
                # Find diameter column
                diameter_col = None
                possible_cols = ['diameter', 'Diameter', 'Diameter (mm)', 'diameter_mm']
                for col in self.diameter_data.columns:
                    if any(dc.lower() in col.lower() for dc in possible_cols):
                        diameter_col = col
                        break
                
                if diameter_col:
                    diameter_values = self.diameter_data[diameter_col].values
                    
                    # If there's a Frame column in diameter data, use it for proper mapping
                    if 'Frame' in self.diameter_data.columns:
                        frame_col = self.diameter_data['Frame'].values
                        # Create full array initialized with NaN
                        full_diameter = np.full(self.total_frames, np.nan)
                        # Fill in available data
                        valid_frames = (frame_col >= 0) & (frame_col < self.total_frames)
                        if np.any(valid_frames):
                            valid_indices = frame_col[valid_frames].astype(int)
                            full_diameter[valid_indices] = diameter_values[valid_frames]
                        self.synced_data['Diameter'] = full_diameter
                        print(f"DEBUG: Used Frame mapping for diameter data")
                    else:
                        # Interpolate to match video frames
                        if len(diameter_values) != self.total_frames:
                            x_old = np.linspace(0, self.total_frames-1, len(diameter_values))
                            x_new = np.arange(self.total_frames)
                            self.synced_data['Diameter'] = np.interp(x_new, x_old, diameter_values)
                            print(f"DEBUG: Interpolated diameter data from {len(diameter_values)} to {self.total_frames} points")
                        else:
                            self.synced_data['Diameter'] = diameter_values[:self.total_frames]
                            print(f"DEBUG: Direct mapping diameter data")
                    
                    print(f"DEBUG: Synced diameter data - {len(diameter_values)} original points")
                else:
                    print(f"DEBUG: No diameter column found in: {list(self.diameter_data.columns)}")
            
            # Try to add pressure data  
            if self.pressure_data is not None and not self.pressure_data.empty:
                pressure_col = None
                possible_cols = ['pressure', 'Pressure', 'sensor', 'Sensor Value']
                for col in self.pressure_data.columns:
                    if any(pc.lower() in col.lower() for pc in possible_cols):
                        pressure_col = col
                        break
                        
                if pressure_col:
                    pressure_values = self.pressure_data[pressure_col].values
                    
                    # Interpolate to match video frames
                    if len(pressure_values) != self.total_frames:
                        x_old = np.linspace(0, self.total_frames-1, len(pressure_values))
                        x_new = np.arange(self.total_frames)
                        self.synced_data['Pressure'] = np.interp(x_new, x_old, pressure_values)
                        print(f"DEBUG: Interpolated pressure data from {len(pressure_values)} to {self.total_frames} points")
                    else:
                        self.synced_data['Pressure'] = pressure_values[:self.total_frames]
                        print(f"DEBUG: Direct mapping pressure data")
                    
                    print(f"DEBUG: Synced pressure data - {len(pressure_values)} original points")
                else:
                    print(f"DEBUG: No pressure column found in: {list(self.pressure_data.columns)}")
            
            # Check if we have any data to plot
            has_diameter = 'Diameter' in self.synced_data.columns
            has_pressure = 'Pressure' in self.synced_data.columns
            
            print(f"DEBUG: Sync result - Diameter: {has_diameter}, Pressure: {has_pressure}")
            print(f"DEBUG: Synced data shape: {self.synced_data.shape}")
                
        except Exception as e:
            print(f"Error syncing data: {e}")
            self.synced_data = None
            
    def display_frame(self):
        """Display current video frame"""
        if not self.cap:
            return
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            # Convert from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get original dimensions
            h, w = frame.shape[:2]
            
            # Scale to fit display without making it larger than original
            max_width, max_height = 600, 500
            if w > max_width or h > max_height:
                scale = min(max_width/w, max_height/h)
                new_w, new_h = int(w*scale), int(h*scale)
                frame = cv2.resize(frame, (new_w, new_h))
            
            # Convert to PIL Image
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)
              # Update display
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
            # Update frame label
            self.frame_label.configure(text=f"{self.current_frame}/{self.total_frames-1}")
            
    def update_plot(self):
        """Update the diameter vs pressure plot"""
        self.ax.clear()
        if hasattr(self, 'ax2') and self.ax2 is not None:
            self.ax2.clear()
        
        if self.synced_data is not None and not self.synced_data.empty:
            frames = self.synced_data['Frame']
            has_diameter = 'Diameter' in self.synced_data.columns
            has_pressure = 'Pressure' in self.synced_data.columns
            
            if has_diameter or has_pressure:
                # Plot available data
                if has_diameter:
                    diameter = self.synced_data['Diameter']
                    # Remove NaN values for plotting
                    valid_frames = ~pd.isna(diameter)
                    if valid_frames.any():
                        self.ax.plot(frames[valid_frames], diameter[valid_frames], 'b-', label='Diameter (mm)', linewidth=1.5)
                        self.ax.set_ylabel('Diameter (mm)', color='blue')
                        self.ax.tick_params(axis='y', labelcolor='blue')
                
                if has_pressure:
                    if has_diameter:
                        # Create secondary y-axis for pressure
                        if not hasattr(self, 'ax2') or self.ax2 is None:
                            self.ax2 = self.ax.twinx()
                        pressure = self.synced_data['Pressure']
                        self.ax2.plot(frames, pressure, 'r-', label='Pressure', linewidth=1.5)
                        self.ax2.set_ylabel('Pressure', color='red')
                        self.ax2.tick_params(axis='y', labelcolor='red')
                    else:
                        # Only pressure data available
                        pressure = self.synced_data['Pressure']
                        self.ax.plot(frames, pressure, 'r-', label='Pressure', linewidth=1.5)
                        self.ax.set_ylabel('Pressure', color='red')
                        self.ax.tick_params(axis='y', labelcolor='red')
                  # Highlight current frame if video is loaded
                if self.total_frames > 0 and self.current_frame < len(frames):
                    if has_diameter and not pd.isna(self.synced_data['Diameter'].iloc[self.current_frame]):
                        current_diameter = self.synced_data['Diameter'].iloc[self.current_frame]
                        self.ax.plot(self.current_frame, current_diameter, 'bo', markersize=8)
                        self.ax.annotate(f'D: {current_diameter:.2f}mm', 
                                       xy=(self.current_frame, current_diameter),
                                       xytext=(10, 10), textcoords='offset points',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='blue', alpha=0.7),
                                       color='white', fontsize=9)
                    
                    if has_pressure:
                        current_pressure = self.synced_data['Pressure'].iloc[self.current_frame]
                        if has_diameter and hasattr(self, 'ax2') and self.ax2 is not None:
                            self.ax2.plot(self.current_frame, current_pressure, 'ro', markersize=8)
                            self.ax2.annotate(f'P: {current_pressure:.2f}', 
                                            xy=(self.current_frame, current_pressure),
                                            xytext=(10, -20), textcoords='offset points',
                                            bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                                            color='white', fontsize=9)
                        else:
                            self.ax.plot(self.current_frame, current_pressure, 'ro', markersize=8)
                            self.ax.annotate(f'P: {current_pressure:.2f}', 
                                           xy=(self.current_frame, current_pressure),
                                           xytext=(10, -20), textcoords='offset points',
                                           bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                                           color='white', fontsize=9)
                
                # Set labels and title
                self.ax.set_xlabel('Frame Number')
                self.ax.set_title('Diameter vs Pressure Analysis')
                self.ax.grid(True, alpha=0.3)
            else:
                # No valid data
                self.ax.text(0.5, 0.5, 'Data loaded but no valid measurements found\nCheck column names in CSV files', 
                            transform=self.ax.transAxes, ha='center', va='center',
                            fontsize=12, color='orange')
                self.ax.set_title('Diameter vs Pressure Analysis')
        else:
            # No data loaded
            message = 'No analysis data available\nSelect a subject with [SUCCESS] Complete status'
            if hasattr(self, 'subject_var') and self.subject_var.get():
                selected = self.subject_var.get()
                if "[ERROR] No Results" in selected:
                    message = 'No inference results found\nRun video inference first'
                elif "[WARN] No Analysis" in selected:
                    message = 'Video available but no diameter analysis\nRun advanced analytics first'
            
            self.ax.text(0.5, 0.5, message, 
                        transform=self.ax.transAxes, ha='center', va='center',
                        fontsize=12, color='gray')
            self.ax.set_title('Diameter vs Pressure Analysis')
        
        self.canvas.draw()
        
    def on_frame_change(self, value):
        """Handle frame slider change"""
        self.current_frame = int(float(value))
        self.display_frame()
        self.update_plot()
        
    def play_video(self):
        """Start video playback"""
        if not self.is_playing and self.cap:
            self.is_playing = True
            self.play_next_frame()
            
    def pause_video(self):
        """Pause video playback"""
        self.is_playing = False
        if self.play_job:
            self.root.after_cancel(self.play_job)
            
    def play_next_frame(self):
        """Play next frame in sequence"""
        if self.is_playing and self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.frame_var.set(self.current_frame)
            self.display_frame()
            self.update_plot()
            self.play_job = self.root.after(50, self.play_next_frame)  # ~20 FPS
        else:
            self.is_playing = False
            
    def __del__(self):
        """Cleanup"""
        if self.cap:
            self.cap.release()

    def setup_menu_with_theme(self):
        """Setup menu bar with theme toggle"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
          # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Subject Data", command=self.load_subject)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Export Plot", command=self.export_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        theme_menu.add_command(label="☀️ Light Mode", 
                              command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="🌙 Dark Mode", 
                              command=lambda: self.set_theme("dark"))
        theme_menu.add_separator()
        theme_menu.add_command(label="🔄 Toggle Theme", 
                              command=self.toggle_theme)
        
        view_menu.add_separator()
        view_menu.add_command(label="Refresh Data", command=self.refresh_subjects)
        view_menu.add_command(label="Reset View", command=self.reset_view)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Analysis", command=self.open_analysis_tools)
        tools_menu.add_command(label="Batch Export", command=self.batch_export)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        if self.theme_manager.set_theme(theme_name):
            self.apply_current_theme()
    
    def toggle_theme(self):
        """Toggle theme and apply"""
        new_theme = self.theme_manager.switch_theme()
        self.apply_current_theme()
        messagebox.showinfo("Theme Changed", f"Theme changed to {new_theme.title()} Mode")
    
    def apply_current_theme(self):
        """Apply current theme to data viewer"""
        # Configure ttk styles first
        self.theme_manager.configure_ttk_style()
        
        # Apply theme to all widgets
        self.theme_manager.apply_theme_recursive(self.root)
          # Update matplotlib plots with theme colors
        self.update_plot_theme()
    
    def update_plot_theme(self):
        """Update matplotlib plots to match theme"""
        if hasattr(self, 'figure') and self.figure and hasattr(self, 'ax') and self.ax:
            theme = self.theme_manager.get_theme()
            
            # Set plot background colors
            self.figure.patch.set_facecolor(theme["bg"])
            self.ax.set_facecolor(theme["frame_bg"])
            
            # Set text colors
            self.ax.tick_params(colors=theme["fg"])
            self.ax.xaxis.label.set_color(theme["fg"])
            self.ax.yaxis.label.set_color(theme["fg"])
            self.ax.title.set_color(theme["fg"])
            
            # Update spines
            for spine in self.ax.spines.values():
                spine.set_color(theme["fg"])
            
            # Update legend if exists
            legend = self.ax.get_legend()
            if legend:
                legend.get_frame().set_facecolor(theme["frame_bg"])
                for text in legend.get_texts():
                    text.set_color(theme["fg"])
            
            # Refresh canvas
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.draw()
    
    def refresh_subjects(self):
        """Refresh available subjects list"""
        self.detect_available_subjects()
        if hasattr(self, 'subject_combo'):
            self.subject_combo['values'] = [f"Subject {i}" for i in range(1, len(self.available_subjects) + 1)]
    
    def reset_view(self):
        """Reset view to default state"""
        if hasattr(self, 'ax') and self.ax:
            self.ax.clear()
            self.canvas.draw()
    
    def open_analysis_tools(self):
        """Open advanced analysis tools"""
        messagebox.showinfo("Analysis Tools", "Advanced analysis tools will be implemented in future version")
    
    def batch_export(self):
        """Batch export functionality"""
        messagebox.showinfo("Batch Export", "Batch export functionality will be implemented in future version")
    
    def export_data(self):
        """Export current data"""
        if self.synced_data is not None:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            if filename:
                if filename.endswith('.xlsx'):
                    self.synced_data.to_excel(filename, index=False)
                else:
                    self.synced_data.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Data exported to {filename}")
        else:
            messagebox.showwarning("Warning", "No data to export")
    
    def export_plot(self):
        """Export current plot"""
        if hasattr(self, 'figure'):
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
            )
            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot exported to {filename}")
        else:
            messagebox.showwarning("Warning", "No plot to export")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """Enhanced Data Viewer - Help

Theme Controls:
• View → Theme → Light/Dark Mode to change themes
• View → Theme → Toggle Theme for quick switch

Data Loading:
• Select subject from dropdown
• Load video and diameter data
• Analyze correlation with pressure data

Keyboard Shortcuts:
• Ctrl+O: Load subject data  
• Ctrl+E: Export data
• Ctrl+T: Toggle theme
• F5: Refresh subjects

Navigation:
• Use video controls to navigate frames
• Plot shows real-time correlation analysis
"""
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""Enhanced Data Viewer v2.0

Current Theme: {self.theme_manager.current_theme.title()}

Features:
• Dark/Light theme support
• Advanced data visualization
• Real-time correlation analysis
• Multi-format export support

Developed for Carotid Artery Analysis
© 2024 Research Project"""
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = EnhancedDataViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

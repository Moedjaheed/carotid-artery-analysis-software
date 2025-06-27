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
import math
from theme_manager import ThemeManager

class ElasticityCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Elasticity Calculator - Carotid Artery Elasticity Analysis")
        self.root.geometry("1800x1200")
        
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
        self.baseline_frame_index = 0
        self.compressed_frame_index = 0
        self.vertical_line1 = None
        self.vertical_line2 = None
        
        # Elasticity calculation variables
        self.baseline_diameter = 0.0
        self.compressed_diameter = 0.0
        self.baseline_pressure = 0.0
        self.compressed_pressure = 0.0
        self.probe_contact_area = 1.0  # cm² - default, user can modify
        
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
    
    def clear_previous_data(self):
        """Clear all previous data before loading new subject"""
        try:
            print("DEBUG: Clearing previous elasticity data...")
            
            # Reset data containers
            self.video_path = None
            self.segmented_video_path = None
            self.diameter_data = None
            self.pressure_data = None
            self.synced_data = None
            
            # Release video capture
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Reset frame variables
            self.current_frame = 0
            self.total_frames = 0
            self.baseline_frame_index = 0
            self.compressed_frame_index = 0
            
            # Reset elasticity variables
            self.baseline_diameter = 0.0
            self.compressed_diameter = 0.0
            self.baseline_pressure = 0.0
            self.compressed_pressure = 0.0
            
            # Clear vertical lines references
            self.vertical_line1 = None
            self.vertical_line2 = None
            
            # Clear and reset the plot
            if hasattr(self, 'ax'):
                self.ax.clear()
                self.ax.text(0.5, 0.5, 'No data loaded\nSelect a subject to begin elasticity analysis', 
                            horizontalalignment='center', verticalalignment='center', 
                            transform=self.ax.transAxes, fontsize=12, color='gray')
                if hasattr(self, 'canvas'):
                    self.canvas.draw()
            
            # Reset frame info labels
            if hasattr(self, 'baseline_info_label'):
                self.baseline_info_label.configure(text="Baseline: Diameter: -- | Pressure: -- N")
            if hasattr(self, 'compressed_info_label'):
                self.compressed_info_label.configure(text="Compressed: Diameter: -- | Pressure: -- N")
            
            # Reset elasticity calculation labels
            if hasattr(self, 'strain_result_label'):
                self.strain_result_label.configure(text="--")
            if hasattr(self, 'pem_result_label'):
                self.pem_result_label.configure(text="--")
            if hasattr(self, 'beta_result_label'):
                self.beta_result_label.configure(text="--")
            if hasattr(self, 'dc_result_label'):
                self.dc_result_label.configure(text="--")
            
            # Reset video displays
            if hasattr(self, 'video1_label'):
                self.video1_label.configure(image='')
                self.video1_label.image = None
            if hasattr(self, 'video2_label'):
                self.video2_label.configure(image='')
                self.video2_label.image = None
            
            # Reset frame labels
            if hasattr(self, 'baseline_frame_label'):
                self.baseline_frame_label.configure(text="0/0")
            if hasattr(self, 'compressed_frame_label'):
                self.compressed_frame_label.configure(text="0/0")
            
            # Reset status
            if hasattr(self, 'status_var'):
                self.status_var.set("Ready - Select a subject to load")
            
            print("DEBUG: Previous elasticity data cleared successfully")
            
        except Exception as e:
            print(f"DEBUG: Error clearing previous elasticity data: {e}")

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subject selection
        ttk.Label(control_frame, text="Select Subject:").pack(side=tk.LEFT, padx=(0, 5))
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(control_frame, textvariable=self.subject_var, 
                                         values=self.available_subjects, state="readonly", width=30)
        self.subject_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_subject_selected)
        
        ttk.Button(control_frame, text="Load Subject", command=self.load_subject).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Browse Folder", command=self.load_subject_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        # Probe contact area setting
        ttk.Label(control_frame, text="Probe Area (cm²):").pack(side=tk.LEFT, padx=(20, 5))
        self.probe_area_var = tk.DoubleVar(value=1.0)
        probe_area_entry = ttk.Entry(control_frame, textvariable=self.probe_area_var, width=10)
        probe_area_entry.pack(side=tk.LEFT, padx=(0, 10))
        probe_area_entry.bind("<KeyRelease>", self.on_probe_area_changed)
        
        # Content frame with notebook for organized layout
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Frame Comparison
        comparison_tab = ttk.Frame(notebook)
        notebook.add(comparison_tab, text="Frame Comparison")
        
        # Video frames section
        video_frame = ttk.LabelFrame(comparison_tab, text="Video Frame Comparison", padding=10)
        video_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Baseline frame (left)
        baseline_frame = ttk.Frame(video_frame)
        baseline_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(baseline_frame, text="Baseline Frame", font=("Arial", 12, "bold")).pack()
        self.video1_label = ttk.Label(baseline_frame, text="No video loaded", anchor="center")
        self.video1_label.pack(pady=5)
        
        # Baseline frame controls
        baseline_controls = ttk.Frame(baseline_frame)
        baseline_controls.pack(fill=tk.X, pady=5)
        
        self.baseline_frame_var = tk.IntVar()
        self.baseline_scale = ttk.Scale(baseline_controls, from_=0, to=100, variable=self.baseline_frame_var, 
                                       orient=tk.HORIZONTAL, command=self.on_baseline_frame_change)
        self.baseline_scale.pack(fill=tk.X, pady=2)
        
        self.baseline_frame_label = ttk.Label(baseline_controls, text="0/0")
        self.baseline_frame_label.pack()
        
        self.baseline_info_label = ttk.Label(baseline_frame, text="Baseline: Diameter: -- | Pressure: -- N", foreground="Purple")
        self.baseline_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Compressed frame (right)
        compressed_frame = ttk.Frame(video_frame)
        compressed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(compressed_frame, text="Compressed Frame", font=("Arial", 12, "bold")).pack()
        self.video2_label = ttk.Label(compressed_frame, text="No video loaded", anchor="center")
        self.video2_label.pack(pady=5)
        
        # Compressed frame controls
        compressed_controls = ttk.Frame(compressed_frame)
        compressed_controls.pack(fill=tk.X, pady=5)
        
        self.compressed_frame_var = tk.IntVar()
        self.compressed_scale = ttk.Scale(compressed_controls, from_=0, to=100, variable=self.compressed_frame_var, 
                                         orient=tk.HORIZONTAL, command=self.on_compressed_frame_change)
        self.compressed_scale.pack(fill=tk.X, pady=2)
        
        self.compressed_frame_label = ttk.Label(compressed_controls, text="0/0")
        self.compressed_frame_label.pack()
        
        self.compressed_info_label = ttk.Label(compressed_frame, text="Compressed: Diameter: -- | Pressure: -- N", foreground="red")
        self.compressed_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Plot section
        plot_frame = ttk.LabelFrame(comparison_tab, text="Diameter vs Pressure Analysis with Frame Indicators", padding=10)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Elasticity Calculations
        elasticity_tab = ttk.Frame(notebook)
        notebook.add(elasticity_tab, text="Elasticity Analysis")
        
        self.setup_elasticity_tab(elasticity_tab)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready - Select a subject to load")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)

    def setup_elasticity_tab(self, parent):
        """Setup the elasticity calculations tab"""
        # Main container
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input parameters frame
        input_frame = ttk.LabelFrame(main_container, text="Measurement Parameters", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Parameters grid
        params_grid = ttk.Frame(input_frame)
        params_grid.pack(fill=tk.X)
        
        # Current measurements display
        row = 0
        ttk.Label(params_grid, text="Current Measurements:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        row += 1
        ttk.Label(params_grid, text="Baseline Diameter:").grid(row=row, column=0, sticky="w", padx=(0, 5))
        self.d_baseline_var = tk.StringVar(value="-- mm")
        ttk.Label(params_grid, textvariable=self.d_baseline_var, foreground="blue").grid(row=row, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(params_grid, text="Compressed Diameter:").grid(row=row, column=2, sticky="w", padx=(0, 5))
        self.d_compressed_var = tk.StringVar(value="-- mm")
        ttk.Label(params_grid, textvariable=self.d_compressed_var, foreground="red").grid(row=row, column=3, sticky="w")
        
        row += 1
        ttk.Label(params_grid, text="Baseline Pressure:").grid(row=row, column=0, sticky="w", padx=(0, 5))
        self.p_baseline_var = tk.StringVar(value="-- N")
        ttk.Label(params_grid, textvariable=self.p_baseline_var, foreground="blue").grid(row=row, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(params_grid, text="Compressed Pressure:").grid(row=row, column=2, sticky="w", padx=(0, 5))
        self.p_compressed_var = tk.StringVar(value="-- N")
        ttk.Label(params_grid, textvariable=self.p_compressed_var, foreground="red").grid(row=row, column=3, sticky="w")
        
        # Calculate button
        row += 1
        calc_button = ttk.Button(params_grid, text="Calculate Elasticity Parameters", command=self.calculate_elasticity)
        calc_button.grid(row=row, column=0, columnspan=4, pady=(15, 10))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_container, text="Elasticity Parameters Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create results grid
        self.setup_results_grid(results_frame)
    
    def setup_results_grid(self, parent):
        """Setup the results display grid"""
        # Main results container
        results_container = ttk.Frame(parent)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Calculations
        left_frame = ttk.Frame(results_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Parameter 1: Strain
        strain_frame = ttk.LabelFrame(left_frame, text="1. Strain (ε)", padding=10)
        strain_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(strain_frame, text="Formula: ε = (D_compressed - D_baseline) / D_baseline").pack(anchor="w")
        ttk.Label(strain_frame, text="Unit: Dimensionless", font=("Arial", 9, "italic")).pack(anchor="w")
        
        strain_result_frame = ttk.Frame(strain_frame)
        strain_result_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(strain_result_frame, text="Result:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.strain_result_label = ttk.Label(strain_result_frame, text="--", font=("Arial", 12, "bold"), foreground="blue")
        self.strain_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Parameter 2: Peterson Elastic Modulus
        pem_frame = ttk.LabelFrame(left_frame, text="2. Peterson Elastic Modulus (PEM)", padding=10)
        pem_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pem_frame, text="Formula: PEM = ΔP / ε = (ΔP × D_baseline) / (D_compressed - D_baseline)").pack(anchor="w")
        ttk.Label(pem_frame, text="Unit: mmHg or N/cm²", font=("Arial", 9, "italic")).pack(anchor="w")
        
        pem_result_frame = ttk.Frame(pem_frame)
        pem_result_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(pem_result_frame, text="Result:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.pem_result_label = ttk.Label(pem_result_frame, text="--", font=("Arial", 12, "bold"), foreground="green")
        self.pem_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right column - More calculations
        right_frame = ttk.Frame(results_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Parameter 3: Stiffness Parameter β
        beta_frame = ttk.LabelFrame(right_frame, text="3. Stiffness Parameter (β)", padding=10)
        beta_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(beta_frame, text="Formula: β = ln(P_compressed / P_baseline) / ε").pack(anchor="w")
        ttk.Label(beta_frame, text="Unit: Dimensionless", font=("Arial", 9, "italic")).pack(anchor="w")
        
        beta_result_frame = ttk.Frame(beta_frame)
        beta_result_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(beta_result_frame, text="Result:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.beta_result_label = ttk.Label(beta_result_frame, text="--", font=("Arial", 12, "bold"), foreground="orange")
        self.beta_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Parameter 4: Distensibility
        dc_frame = ttk.LabelFrame(right_frame, text="4. Distensibility (DC)", padding=10)
        dc_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dc_frame, text="Formula: DC = 2(D_compressed - D_baseline) / (D_baseline × ΔP)").pack(anchor="w")
        ttk.Label(dc_frame, text="Unit: Pa⁻¹ (× 10⁻⁵)", font=("Arial", 9, "italic")).pack(anchor="w")
        
        dc_result_frame = ttk.Frame(dc_frame)
        dc_result_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(dc_result_frame, text="Result:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.dc_result_label = ttk.Label(dc_result_frame, text="--", font=("Arial", 12, "bold"), foreground="purple")
        self.dc_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Clinical interpretation frame
        interpretation_frame = ttk.LabelFrame(results_container, text="Clinical Interpretation", padding=10)
        interpretation_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.interpretation_text = tk.Text(interpretation_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.interpretation_text.pack(fill=tk.X)
        
        # Scrollbar for interpretation text
        scrollbar = ttk.Scrollbar(interpretation_frame, orient=tk.VERTICAL, command=self.interpretation_text.yview)
        self.interpretation_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_menu_with_theme(self):
        """Setup menu bar with theme support"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Subject", command=self.load_subject)
        file_menu.add_command(label="Browse Folder", command=self.load_subject_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Calculate Elasticity", command=self.calculate_elasticity)
        analysis_menu.add_command(label="Reset Calculations", command=self.reset_calculations)
          # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Change Theme", command=self.change_theme)
        view_menu.add_command(label="Show Help", command=self.show_help)
    
    def apply_current_theme(self):
        """Apply current theme to all components"""
        try:
            # Apply theme to main window
            self.theme_manager.apply_theme_recursive(self.root)
            
            # Update matplotlib plots if they exist
            self.update_matplotlib_theme()
        except Exception as e:
            print(f"Theme application error: {e}")
    
    def update_matplotlib_theme(self):
        """Update matplotlib plots to match current theme"""
        try:
            # Update matplotlib rcParams for new plots
            mpl_style = self.theme_manager.get_matplotlib_style()
            for key, value in mpl_style.items():
                if key != 'axes.prop_cycle':
                    plt.rcParams[key] = value
                else:
                    # Handle prop_cycle separately
                    try:
                        from cycler import cycler
                        if self.theme_manager.current_theme == "dark":
                            colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0', '#00BCD4']
                        else:
                            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                        plt.rcParams['axes.prop_cycle'] = cycler('color', colors)
                    except ImportError:
                        print("DEBUG: cycler not available, using default colors")
        except Exception as e:
            print(f"DEBUG: Error updating matplotlib theme: {e}")
    
    def change_theme(self):
        """Toggle between light and dark themes"""
        try:
            self.theme_manager.toggle_theme()
            self.apply_current_theme()
            
            # Redraw plot if data exists
            if hasattr(self, 'synced_data') and self.synced_data is not None:
                self.update_plot()
        except Exception as e:
            print(f"Error changing theme: {e}")
    
    def on_subject_selected(self, event=None):
        """Handle subject selection from combobox"""
        selected = self.subject_var.get()
        if selected and not selected.startswith("No") and not selected.startswith("Error"):
            # Extract subject name (remove status part)
            subject_name = selected.split(" [")[0]
            subject_path = os.path.join("data_uji", subject_name)
            if os.path.exists(subject_path):
                self.load_subject_from_path(subject_path)
    
    def load_subject(self):
        """Load subject data via combobox selection"""
        selected = self.subject_var.get()
        if not selected or selected.startswith("No") or selected.startswith("Error"):
            messagebox.showwarning("Warning", "Please select a valid subject from the dropdown")
            return
        
        # Extract subject name and load
        subject_name = selected.split(" [")[0]
        subject_path = os.path.join("data_uji", subject_name)
        self.load_subject_from_path(subject_path)
    
    def load_subject_folder(self):
        """Load subject data via folder browser"""
        folder = filedialog.askdirectory(title="Select Subject Folder")
        if not folder:
            return
        self.load_subject_from_path(folder)
    
    def load_subject_from_path(self, folder):
        """Load subject data from specified path"""
        try:
            # Clear previous data first
            self.clear_previous_data()
            
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
            self.baseline_scale.configure(to=self.total_frames-1)
            self.compressed_scale.configure(to=self.total_frames-1)
            
            # Set initial frame positions            self.baseline_frame_var.set(0)
            self.compressed_frame_var.set(min(self.total_frames-1, self.total_frames//2))
            self.baseline_frame_index = 0
            self.compressed_frame_index = min(self.total_frames-1, self.total_frames//2)
            
            # Load diameter data (includes pressure mapping if needed)
            self.load_diameter_data(subject_name)
            
            # Sync data
            self.sync_data()
            
            # Display frames and update plot
            self.display_frames()
            self.update_plot()
            self.update_frame_info()
            
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
            error_msg = f"Error loading subject: {str(e)}"
            print(f"DEBUG: {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error loading subject")
    
    def load_diameter_data(self, subject_name):
        """Load diameter data from CSV files"""
        try:
            # Look for diameter data in inference_results folder
            inference_folder = os.path.join("inference_results", subject_name)
            if not os.path.exists(inference_folder):
                print("DEBUG: No inference folder found")
                return
            
            # Look for diameter CSV files
            diameter_files = glob.glob(os.path.join(inference_folder, "*.csv"))
            
            if not diameter_files:
                print("DEBUG: No CSV files found in inference folder")
                return
            
            # Prioritize files with pressure data (already combined)
            pressure_files = [f for f in diameter_files if 'pressure' in f.lower()]
            if pressure_files:
                self.diameter_data = pd.read_csv(pressure_files[0])
                print(f"DEBUG: Loaded diameter data with pressure: {len(self.diameter_data)} rows")
                print(f"DEBUG: Found pressure data in {os.path.basename(pressure_files[0])}")
            else:
                # Use the first diameter CSV file found
                self.diameter_data = pd.read_csv(diameter_files[0])
                print(f"DEBUG: Loaded diameter data: {len(self.diameter_data)} rows")
                
                # Try to load separate pressure data
                self.load_separate_pressure_data(subject_name)
            
            print(f"DEBUG: Diameter columns: {list(self.diameter_data.columns)}")
            
            # Standardize column names for diameter
            diameter_columns = ['Diameter (mm)', 'Diameter', 'diameter', 'avg_diameter']
            diameter_col_found = None
            
            for col in diameter_columns:
                if col in self.diameter_data.columns:
                    diameter_col_found = col
                    break
            
            if diameter_col_found:
                if diameter_col_found != 'diameter':
                    self.diameter_data['diameter'] = self.diameter_data[diameter_col_found]
                    print(f"DEBUG: Standardized diameter column from '{diameter_col_found}' to 'diameter'")
                  # Validate diameter data
                valid_diameter = pd.to_numeric(self.diameter_data['diameter'], errors='coerce').notna()
                print(f"DEBUG: {valid_diameter.sum()} valid diameter measurements")
                
        except Exception as e:
            print(f"DEBUG: Error loading diameter data: {e}")
            self.diameter_data = None
    
    def load_separate_pressure_data(self, subject_name):
        """Load pressure data using timestamp synchronization for accurate alignment"""
        try:
            # Look for pressure data in data_uji folder
            data_uji_folder = os.path.join("data_uji", subject_name)
            if not os.path.exists(data_uji_folder):
                print("DEBUG: No data_uji folder found for pressure data")
                return
            
            # Load pressure data
            subject_files = glob.glob(os.path.join(data_uji_folder, f"{subject_name.lower()}.csv"))
            if not subject_files:
                subject_files = glob.glob(os.path.join(data_uji_folder, "subject*.csv"))
                if not subject_files:
                    print("DEBUG: No pressure data files found")
                    return
            
            pressure_df = pd.read_csv(subject_files[0])
            print(f"DEBUG: Loaded pressure data: {len(pressure_df)} rows")
            print(f"DEBUG: Pressure columns: {list(pressure_df.columns)}")
            
            # Load timestamp mapping file
            timestamp_file = os.path.join(data_uji_folder, "timestamps.csv")
            if not os.path.exists(timestamp_file):
                print("DEBUG: No timestamps.csv found - using fallback interpolation")
                self._fallback_pressure_mapping(subject_name)
                return
            
            timestamp_df = pd.read_csv(timestamp_file)
            print(f"DEBUG: Loaded timestamp data: {len(timestamp_df)} rows")
            
            # Parse and synchronize timestamps
            success = self._synchronize_pressure_with_image_timestamps(pressure_df, timestamp_df)
            
            if not success:
                print("DEBUG: Timestamp synchronization failed - using fallback")
                self._fallback_pressure_mapping(subject_name)
                
        except Exception as e:
            print(f"DEBUG: Error in timestamp-based synchronization: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to interpolation method
            self._fallback_pressure_mapping(subject_name)
    
    def _synchronize_pressure_with_image_timestamps(self, pressure_df, timestamp_df):
        """Synchronize pressure data with image timestamps using relative timing"""
        try:
            print("DEBUG: Starting improved timestamp synchronization...")
            
            # Parse pressure timestamps (format: HH-MM-SS-mmm)
            pressure_times_abs = []
            pressure_values = []
            
            for _, row in pressure_df.iterrows():
                timestamp_str = str(row.iloc[0])  # First column is timestamp
                pressure_val = float(row.iloc[1])  # Second column is sensor value
                
                try:
                    # Parse HH-MM-SS-mmm format
                    parts = timestamp_str.split('-')
                    if len(parts) == 4:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = int(parts[2])
                        milliseconds = int(parts[3])
                        
                        # Convert to total seconds (absolute time)
                        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
                        pressure_times_abs.append(total_seconds)
                        pressure_values.append(pressure_val)
                except:
                    continue
            
            print(f"DEBUG: Parsed {len(pressure_times_abs)} pressure timestamps")
            if len(pressure_times_abs) == 0:
                return False
            
            # Parse image timestamps (format: HH:MM:SS.mmm)
            image_times_abs = []
            image_frames = []
            
            for _, row in timestamp_df.iterrows():
                if 'Frame Number' in timestamp_df.columns and 'Timestamp' in timestamp_df.columns:
                    frame_num = row['Frame Number']
                    timestamp_str = str(row['Timestamp'])
                    
                    try:
                        # Parse HH:MM:SS.mmm format
                        parts = timestamp_str.split(':')
                        if len(parts) == 3:
                            hours = int(parts[0])
                            minutes = int(parts[1])
                            sec_parts = parts[2].split('.')
                            seconds = int(sec_parts[0])
                            milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
                            
                            # Convert to total seconds (absolute time)
                            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
                            image_times_abs.append(total_seconds)
                            image_frames.append(frame_num)
                    except:
                        continue
            
            print(f"DEBUG: Parsed {len(image_times_abs)} image timestamps")
            if len(image_times_abs) == 0:
                return False
            
            # Convert to numpy arrays for easier manipulation
            pressure_times_abs = np.array(pressure_times_abs)
            pressure_values = np.array(pressure_values)
            image_times_abs = np.array(image_times_abs)
            image_frames = np.array(image_frames)
            
            # Calculate time ranges and overlap
            pressure_start = pressure_times_abs.min()
            pressure_end = pressure_times_abs.max()
            image_start = image_times_abs.min()
            image_end = image_times_abs.max()
            
            print(f"DEBUG: Pressure time range: {pressure_start:.3f} - {pressure_end:.3f} ({pressure_end-pressure_start:.3f}s)")
            print(f"DEBUG: Image time range: {image_start:.3f} - {image_end:.3f} ({image_end-image_start:.3f}s)")
            print(f"DEBUG: Time offset: {image_start - pressure_start:.3f}s")
            
            # Find overlap range
            overlap_start = max(pressure_start, image_start)
            overlap_end = min(pressure_end, image_end)
            
            print(f"DEBUG: Overlap range: {overlap_start:.3f} - {overlap_end:.3f} ({overlap_end-overlap_start:.3f}s)")
            
            if overlap_end <= overlap_start:
                print("DEBUG: No time overlap - using interpolation/extrapolation")
                return self._interpolate_pressure_for_all_frames(pressure_times_abs, pressure_values, 
                                                               image_times_abs, image_frames)
            
            # Method 1: Try direct timestamp matching for overlapping region
            synced_data_method1 = []
            
            for i, (img_time, frame_num) in enumerate(zip(image_times_abs, image_frames)):
                if overlap_start <= img_time <= overlap_end:
                    # Find closest pressure measurement
                    time_diffs = np.abs(pressure_times_abs - img_time)
                    closest_idx = np.argmin(time_diffs)
                    min_time_diff = time_diffs[closest_idx]
                    
                    # Only use if time difference is reasonable (< 0.1 second)
                    if min_time_diff < 0.1:
                        synced_data_method1.append((frame_num, pressure_values[closest_idx]))
            
            print(f"DEBUG: Method 1 (direct matching): {len(synced_data_method1)} synchronized points")
            
            # Method 2: Use interpolation for better coverage
            synced_data_method2 = self._interpolate_pressure_for_frames(pressure_times_abs, pressure_values,
                                                                      image_times_abs, image_frames)
            
            # Choose the best method
            if len(synced_data_method1) > len(image_frames) * 0.5:  # If we have good coverage
                print("DEBUG: Using direct timestamp matching")
                synced_pressure_data = synced_data_method1
            else:
                print("DEBUG: Using interpolation method for better coverage")
                synced_pressure_data = synced_data_method2
            
            # Apply to diameter data
            if len(synced_pressure_data) > 0 and self.diameter_data is not None:
                pressure_map = {int(frame): pressure for frame, pressure in synced_pressure_data}
                
                # Apply to diameter data with intelligent fallback
                pressure_column = []
                mapped_count = 0
                
                for _, row in self.diameter_data.iterrows():
                    frame_num = int(row['Frame'])
                    
                    if frame_num in pressure_map:
                        pressure_val = pressure_map[frame_num]
                        mapped_count += 1
                    else:
                        # Intelligent fallback: interpolate from nearby frames
                        pressure_val = self._get_interpolated_pressure(frame_num, pressure_map)
                    
                    pressure_column.append(pressure_val)
                
                self.diameter_data['pressure'] = pressure_column
                
                print(f"DEBUG: Applied pressure to {mapped_count} diameter measurements (direct)")
                print(f"DEBUG: Total diameter measurements: {len(pressure_column)}")
                
                # Show sample synchronized data
                print("DEBUG: Sample synchronized data:")
                sample_count = min(5, len(synced_pressure_data))
                for i in range(sample_count):
                    frame, pressure = synced_pressure_data[i]
                    print(f"  Frame {frame}: Pressure={pressure:.3f} N")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"DEBUG: Error in improved pressure-image synchronization: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _interpolate_pressure_for_frames(self, pressure_times, pressure_values, image_times, image_frames):
        """Interpolate pressure values for image frames"""
        try:
            synced_data = []
            
            # Use numpy interpolation for smooth pressure mapping
            for img_time, frame_num in zip(image_times, image_frames):
                # Interpolate pressure at this time point
                if img_time >= pressure_times.min() and img_time <= pressure_times.max():
                    pressure_val = np.interp(img_time, pressure_times, pressure_values)
                    synced_data.append((frame_num, pressure_val))
                else:
                    # Extrapolate using nearest value
                    if img_time < pressure_times.min():
                        pressure_val = pressure_values[0]  # Use first value
                    else:
                        pressure_val = pressure_values[-1]  # Use last value
                    synced_data.append((frame_num, pressure_val))
            
            print(f"DEBUG: Interpolation method: {len(synced_data)} points")
            return synced_data
            
        except Exception as e:
            print(f"DEBUG: Error in pressure interpolation: {e}")
            return []
    
    def _interpolate_pressure_for_all_frames(self, pressure_times, pressure_values, image_times, image_frames):
        """Fallback interpolation when no overlap exists"""
        try:
            print("DEBUG: Using fallback interpolation (no overlap)")
            
            # Scale pressure timeline to match image timeline
            pressure_duration = pressure_times.max() - pressure_times.min()
            image_duration = image_times.max() - image_times.min()
            
            if pressure_duration > 0 and image_duration > 0:
                # Time-scale the pressure data to match image duration
                scaled_pressure_times = pressure_times.min() + (pressure_times - pressure_times.min()) * (image_duration / pressure_duration)
                
                # Shift to align with image start time
                shifted_pressure_times = scaled_pressure_times - scaled_pressure_times.min() + image_times.min()
                
                # Interpolate
                synced_data = []
                for img_time, frame_num in zip(image_times, image_frames):
                    pressure_val = np.interp(img_time, shifted_pressure_times, pressure_values)
                    synced_data.append((frame_num, pressure_val))
                
                print(f"DEBUG: Fallback interpolation: {len(synced_data)} points")
                return synced_data
            
            return []
            
        except Exception as e:
            print(f"DEBUG: Error in fallback interpolation: {e}")
            return []
    
    def _get_interpolated_pressure(self, target_frame, pressure_map):
        """Get interpolated pressure for a frame not in the map"""
        try:
            if not pressure_map:
                return 0.0
            
            frames = sorted(pressure_map.keys())
            
            # If target frame is outside range, use nearest value
            if target_frame <= frames[0]:
                return pressure_map[frames[0]]
            if target_frame >= frames[-1]:
                return pressure_map[frames[-1]]
            
            # Find surrounding frames for interpolation
            lower_frame = None
            upper_frame = None
            
            for frame in frames:
                if frame <= target_frame:
                    lower_frame = frame
                elif frame > target_frame and upper_frame is None:
                    upper_frame = frame
                    break
            
            if lower_frame is not None and upper_frame is not None:
                # Linear interpolation
                lower_pressure = pressure_map[lower_frame]
                upper_pressure = pressure_map[upper_frame]
                ratio = (target_frame - lower_frame) / (upper_frame - lower_frame)
                return lower_pressure + ratio * (upper_pressure - lower_pressure)
            
            # Fallback to nearest available value
            return pressure_map[frames[0]] if frames else 0.0
            
        except Exception as e:
            print(f"DEBUG: Error in pressure interpolation for frame {target_frame}: {e}")
            return 0.0
    
    def on_baseline_frame_change(self, value):
        """Handle baseline frame slider change"""
        self.baseline_frame_index = int(float(value))
        self.display_frames()
        self.update_plot()
        self.update_frame_info()
    
    def on_compressed_frame_change(self, value):
        """Handle compressed frame slider change"""
        self.compressed_frame_index = int(float(value))
        self.display_frames()
        self.update_plot()
        self.update_frame_info()
    
    def on_probe_area_changed(self, event=None):
        """Handle probe contact area change"""
        try:
            self.probe_contact_area = self.probe_area_var.get()
            # Recalculate elasticity if data is available
            if hasattr(self, 'baseline_diameter') and self.baseline_diameter > 0:
                self.calculate_elasticity()
        except Exception as e:
            print(f"DEBUG: Error updating probe area: {e}")
    
    def display_frames(self):
        """Display the selected baseline and compressed frames"""
        try:
            if not self.cap or self.total_frames == 0:
                return
            
            # Display baseline frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.baseline_frame_index)
            ret1, frame1 = self.cap.read()
            
            if ret1:
                # Resize and convert baseline frame
                frame1_resized = cv2.resize(frame1, (350, 350))
                frame1_rgb = cv2.cvtColor(frame1_resized, cv2.COLOR_BGR2RGB)
                frame1_pil = Image.fromarray(frame1_rgb)
                frame1_tk = ImageTk.PhotoImage(frame1_pil)
                
                self.video1_label.configure(image=frame1_tk)
                self.video1_label.image = frame1_tk  # Keep a reference
            
            # Display compressed frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.compressed_frame_index)
            ret2, frame2 = self.cap.read()
            
            if ret2:
                # Resize and convert compressed frame
                frame2_resized = cv2.resize(frame2, (350, 350))
                frame2_rgb = cv2.cvtColor(frame2_resized, cv2.COLOR_BGR2RGB)
                frame2_pil = Image.fromarray(frame2_rgb)
                frame2_tk = ImageTk.PhotoImage(frame2_pil)
                
                self.video2_label.configure(image=frame2_tk)
                self.video2_label.image = frame2_tk  # Keep a reference
            
            # Update frame labels
            self.baseline_frame_label.configure(text=f"{self.baseline_frame_index}/{self.total_frames-1}")
            self.compressed_frame_label.configure(text=f"{self.compressed_frame_index}/{self.total_frames-1}")
            
        except Exception as e:
            print(f"DEBUG: Error displaying frames: {e}")
    
    def update_frame_info(self):
        """Update frame information display"""
        if self.synced_data is None:
            self.baseline_info_label.configure(text="Baseline: Diameter: -- | Pressure: -- N")
            self.compressed_info_label.configure(text="Compressed: Diameter: -- | Pressure: -- N")
            return
        
        try:
            # Get data for baseline frame
            baseline_data = self.synced_data[self.synced_data['frame'] == self.baseline_frame_index]
            if baseline_data.empty:
                # Find closest frame
                closest_idx = (self.synced_data['frame'] - self.baseline_frame_index).abs().idxmin()
                baseline_data = self.synced_data.loc[[closest_idx]]
                print(f"DEBUG: Using closest frame for baseline: {self.synced_data.loc[closest_idx, 'frame']}")
            
            if not baseline_data.empty:
                # Try different diameter column names
                diameter1 = '--'
                for col in ['diameter', 'Diameter (mm)', 'Diameter', 'avg_diameter']:
                    if col in baseline_data.columns:
                        val = baseline_data.iloc[0].get(col, '--')
                        if val != '--' and pd.notna(val):
                            diameter1 = f"{float(val):.2f}"
                            self.baseline_diameter = float(val)
                            break
                
                pressure1 = baseline_data.iloc[0].get('pressure', '--')
                if pressure1 != '--' and pd.notna(pressure1):
                    pressure1_val = f"{float(pressure1):.2f} N"
                    self.baseline_pressure = float(pressure1)
                else:
                    pressure1_val = "-- N"
                    self.baseline_pressure = 0.0
                
                baseline_info = f"Baseline: Diameter: {diameter1} | Pressure: {pressure1_val}"
            else:
                baseline_info = "Baseline: Diameter: -- | Pressure: -- N"
                self.baseline_diameter = 0.0
                self.baseline_pressure = 0.0
            
            # Get data for compressed frame
            compressed_data = self.synced_data[self.synced_data['frame'] == self.compressed_frame_index]
            if compressed_data.empty:
                # Find closest frame
                closest_idx = (self.synced_data['frame'] - self.compressed_frame_index).abs().idxmin()
                compressed_data = self.synced_data.loc[[closest_idx]]
                print(f"DEBUG: Using closest frame for compressed: {self.synced_data.loc[closest_idx, 'frame']}")
            
            if not compressed_data.empty:
                # Try different diameter column names
                diameter2 = '--'
                for col in ['diameter', 'Diameter (mm)', 'Diameter', 'avg_diameter']:
                    if col in compressed_data.columns:
                        val = compressed_data.iloc[0].get(col, '--')
                        if val != '--' and pd.notna(val):
                            diameter2 = f"{float(val):.2f}"
                            self.compressed_diameter = float(val)
                            break
                
                pressure2 = compressed_data.iloc[0].get('pressure', '--')
                if pressure2 != '--' and pd.notna(pressure2):
                    pressure2_val = f"{float(pressure2):.2f} N"
                    self.compressed_pressure = float(pressure2)
                else:
                    pressure2_val = "-- N"
                    self.compressed_pressure = 0.0
                
                compressed_info = f"Compressed: Diameter: {diameter2} | Pressure: {pressure2_val}"
            else:
                compressed_info = "Compressed: Diameter: -- | Pressure: -- N"
                self.compressed_diameter = 0.0
                self.compressed_pressure = 0.0
            
            self.baseline_info_label.configure(text=baseline_info)
            self.compressed_info_label.configure(text=compressed_info)
            
            # Update elasticity tab parameters
            if hasattr(self, 'd_baseline_var'):
                self.d_baseline_var.set(f"{self.baseline_diameter:.2f} mm" if self.baseline_diameter > 0 else "-- mm")
                self.d_compressed_var.set(f"{self.compressed_diameter:.2f} mm" if self.compressed_diameter > 0 else "-- mm")
                self.p_baseline_var.set(f"{self.baseline_pressure:.2f} N" if self.baseline_pressure > 0 else "-- N")
                self.p_compressed_var.set(f"{self.compressed_pressure:.2f} N" if self.compressed_pressure > 0 else "-- N")            
        except Exception as e:
            print(f"DEBUG: Error updating frame info: {e}")
            self.baseline_info_label.configure(text="Baseline: Diameter: -- | Pressure: -- N")
            self.compressed_info_label.configure(text="Compressed: Diameter: -- | Pressure: -- N")
    
    def update_plot(self):
        """Update the plot with dual vertical lines using timestamp as X-axis"""
        # Clear the plot completely
        self.ax.clear()
        
        # Clear any secondary axes that might exist
        if hasattr(self, 'ax') and hasattr(self.ax, 'figure'):
            # Remove all axes from the figure and recreate the main one
            self.ax.figure.clear()
            self.ax = self.ax.figure.add_subplot(111)
        
        # Reset vertical line references
        self.vertical_line1 = None
        self.vertical_line2 = None
        
        if self.synced_data is None or self.synced_data.empty:
            self.ax.text(0.5, 0.5, 'No data available\nLoad a subject to view analysis', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        try:
            # Debug: Print available columns
            print(f"DEBUG: Available columns for plotting: {list(self.synced_data.columns)}")
            
            # Determine X-axis data (prefer timestamp over frame)
            use_timestamp = 'time_seconds' in self.synced_data.columns and self.synced_data['time_seconds'].notna().any()
            x_data_column = 'time_seconds' if use_timestamp else 'frame'
            x_label = 'Time (seconds)' if use_timestamp else 'Frame Number'
            
            if use_timestamp:
                print("DEBUG: Using timestamp as X-axis")
            else:
                print("DEBUG: Using frame number as X-axis (timestamp not available)")
            
            # Plot diameter data
            diameter_plotted = False
            if 'diameter' in self.synced_data.columns:
                diameter_values = pd.to_numeric(self.synced_data['diameter'], errors='coerce')
                valid_diameter = ~diameter_values.isna()
                
                print(f"DEBUG: Found {valid_diameter.sum()} valid diameter values out of {len(diameter_values)}")
                
                if valid_diameter.any():
                    x_values = self.synced_data.loc[valid_diameter, x_data_column]
                    diameters = diameter_values[valid_diameter]
                    
                    # Remove rows where X values are NaN
                    valid_x = ~pd.to_numeric(x_values, errors='coerce').isna()
                    if valid_x.any():
                        x_values = x_values[valid_x]
                        diameters = diameters[valid_x.values]
                        
                        print(f"DEBUG: Plotting diameter - X range: {x_values.min():.2f}-{x_values.max():.2f}, Diameter range: {diameters.min():.2f}-{diameters.max():.2f}")
                        
                        # Try to find proper column name for label
                        col_name = 'Diameter (mm)'
                        if 'Diameter (mm)' in self.synced_data.columns:
                            col_name = 'Diameter (mm)'
                        elif 'Diameter' in self.synced_data.columns:
                            col_name = 'Diameter'
                        
                        self.ax.plot(x_values, diameters, 'b-', linewidth=2, label=f'{col_name}', alpha=0.8)
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
                    
                    x_values = self.synced_data.loc[valid_pressure, x_data_column]
                    pressures = pressure_values[valid_pressure]
                    
                    # Remove rows where X values are NaN
                    valid_x = ~pd.to_numeric(x_values, errors='coerce').isna()
                    if valid_x.any():
                        x_values = x_values[valid_x]
                        pressures = pressures[valid_x.values]
                        
                        print(f"DEBUG: Plotting pressure - X range: {x_values.min():.2f}-{x_values.max():.2f}, Pressure range: {pressures.min():.2f}-{pressures.max():.2f}")
                        ax2.plot(x_values, pressures, 'g--', linewidth=2, label='Pressure', alpha=0.8)
                        ax2.set_ylabel('Pressure (N)', color='g')
                        ax2.tick_params(axis='y', labelcolor='g')
                        pressure_plotted = True
            
            # If no data was plotted, show sample data or message
            if not diameter_plotted and not pressure_plotted:
                # Create sample data for visualization
                x_values = self.synced_data[x_data_column]
                self.ax.plot(x_values, [50] * len(x_values), 'r--', alpha=0.3, label='No data - sample line')
                self.ax.text(0.5, 0.5, 'No valid data to plot\nCheck data files and columns', 
                            horizontalalignment='center', verticalalignment='center', 
                            transform=self.ax.transAxes, fontsize=10, color='red')
            
            # Add vertical lines for selected frames (convert frame to timestamp if needed)
            if hasattr(self, 'baseline_frame_index'):
                baseline_x = self.get_x_value_for_frame(self.baseline_frame_index, use_timestamp)
                if baseline_x is not None:
                    self.vertical_line1 = self.ax.axvline(x=baseline_x, color='purple', 
                                                         linestyle='-', linewidth=2, alpha=0.7, 
                                                         label=f'Baseline Frame {self.baseline_frame_index}')
            
            if hasattr(self, 'compressed_frame_index'):
                compressed_x = self.get_x_value_for_frame(self.compressed_frame_index, use_timestamp)
                if compressed_x is not None:
                    self.vertical_line2 = self.ax.axvline(x=compressed_x, color='red', 
                                                         linestyle='-', linewidth=2, alpha=0.7, 
                                                         label=f'Compressed Frame {self.compressed_frame_index}')
            
            # Set axis limits - Always start from 0 and show all data
            if not self.synced_data.empty:
                x_values = pd.to_numeric(self.synced_data[x_data_column], errors='coerce').dropna()
                if len(x_values) > 0:
                    x_min = x_values.min()
                    x_max = x_values.max()
                    
                    # Add some padding
                    total_range = x_max - x_min
                    padding = max(0.1 if use_timestamp else 5, total_range * 0.02)  # 2% padding
                    
                    self.ax.set_xlim(x_min - padding, x_max + padding)
                    
                    # Set y-axis limits for better visualization
                    if diameter_plotted:
                        diameter_values = pd.to_numeric(self.synced_data['diameter'], errors='coerce')
                        valid_diameters = diameter_values.dropna()
                        if len(valid_diameters) > 0:
                            y_min = valid_diameters.min() * 0.95
                            y_max = valid_diameters.max() * 1.05
                            self.ax.set_ylim(y_min, y_max)
            
        except Exception as e:
            print(f"DEBUG: Error in update_plot: {e}")
            self.ax.text(0.5, 0.5, f'Error plotting data:\n{str(e)}', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=10, color='red')
        
        # Set labels and title
        self.ax.set_xlabel(x_label)
        title = 'Diameter and Pressure vs Time - Elasticity Analysis' if use_timestamp else 'Diameter and Pressure vs Frame - Elasticity Analysis'
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        
        # Draw the plot
        self.canvas.draw()
    
    def calculate_elasticity(self):
        """Calculate all elasticity parameters"""
        try:
            # Check if we have valid data
            if (self.baseline_diameter <= 0 or self.compressed_diameter <= 0 or 
                self.baseline_pressure < 0 or self.compressed_pressure < 0):
                messagebox.showwarning("Warning", "Please select valid baseline and compressed frames with measurement data")
                return
            
            # Get values
            d_baseline = self.baseline_diameter  # mm
            d_compressed = self.compressed_diameter  # mm
            p_baseline = self.baseline_pressure  # N
            p_compressed = self.compressed_pressure  # N
            
            # Convert pressure from N to N/cm² using probe contact area
            area_cm2 = self.probe_contact_area  # cm²
            p_baseline_Pa = (p_baseline / area_cm2) * 10000  # Convert N/cm² to Pa (1 N/cm² = 10000 Pa)
            p_compressed_Pa = (p_compressed / area_cm2) * 10000
            
            # Convert to mmHg (1 Pa = 0.00750062 mmHg)
            p_baseline_mmHg = p_baseline_Pa * 0.00750062
            p_compressed_mmHg = p_compressed_Pa * 0.00750062
            
            delta_p_mmHg = p_compressed_mmHg - p_baseline_mmHg
            delta_p_Pa = p_compressed_Pa - p_baseline_Pa
            
            # 1. Calculate Strain (ε)
            strain = (d_compressed - d_baseline) / d_baseline
            
            # 2. Calculate Peterson Elastic Modulus (PEM)
            if abs(strain) > 1e-10:  # Avoid division by zero
                pem_mmHg = delta_p_mmHg / strain
                pem_Pa = delta_p_Pa / strain
            else:
                pem_mmHg = float('inf')
                pem_Pa = float('inf')
            
            # 3. Calculate Stiffness Parameter β
            if p_baseline_mmHg > 0 and abs(strain) > 1e-10:
                beta = math.log(p_compressed_mmHg / p_baseline_mmHg) / strain
            else:
                beta = float('inf')
            
            # 4. Calculate Distensibility (DC)
            if abs(delta_p_Pa) > 1e-10:
                # DC = 2(D_compressed - D_baseline) / (D_baseline × ΔP)
                # Convert diameter from mm to m for proper units
                d_baseline_m = d_baseline / 1000  # mm to m
                d_compressed_m = d_compressed / 1000  # mm to m
                dc_pa_inv = 2 * (d_compressed_m - d_baseline_m) / (d_baseline_m * delta_p_Pa)
                dc_scaled = dc_pa_inv * 1e5  # Scale to × 10⁻⁵ Pa⁻¹
            else:
                dc_scaled = float('inf')
            
            # Update result labels
            if strain != float('inf'):
                self.strain_result_label.configure(text=f"{strain:.6f}")
            else:
                self.strain_result_label.configure(text="∞")
            
            if pem_mmHg != float('inf'):
                self.pem_result_label.configure(text=f"{pem_mmHg:.2f} mmHg")
            else:
                self.pem_result_label.configure(text="∞")
            
            if beta != float('inf'):
                self.beta_result_label.configure(text=f"{beta:.2f}")
            else:
                self.beta_result_label.configure(text="∞")
            
            if dc_scaled != float('inf'):
                self.dc_result_label.configure(text=f"{dc_scaled:.2f} × 10⁻⁵ Pa⁻¹")
            else:
                self.dc_result_label.configure(text="∞")
            
            # Update clinical interpretation
            self.update_clinical_interpretation(strain, pem_mmHg, beta, dc_scaled)
            
            print(f"DEBUG: Elasticity calculated - Strain: {strain:.6f}, PEM: {pem_mmHg:.2f} mmHg, β: {beta:.2f}, DC: {dc_scaled:.2f}")
            
        except Exception as e:
            error_msg = f"Error calculating elasticity: {str(e)}"
            print(f"DEBUG: {error_msg}")
            messagebox.showerror("Calculation Error", error_msg)
    
    def update_clinical_interpretation(self, strain, pem, beta, dc):
        """Update clinical interpretation based on calculated values"""
        try:
            self.interpretation_text.configure(state=tk.NORMAL)
            self.interpretation_text.delete(1.0, tk.END)
            
            interpretation = "CLINICAL INTERPRETATION:\n\n"
            
            # Strain interpretation
            interpretation += f"1. STRAIN (ε = {strain:.6f}):\n"
            if strain > 0:
                interpretation += "   • Positive strain indicates artery compression/deformation\n"
                if strain > 0.1:
                    interpretation += "   • High deformation - may indicate reduced vessel stiffness\n"
                elif strain > 0.05:
                    interpretation += "   • Moderate deformation - normal elasticity range\n"
                else:
                    interpretation += "   • Low deformation - may indicate increased stiffness\n"
            else:
                interpretation += "   • Negative or zero strain - check measurement validity\n"
            
            interpretation += "\n"
            
            # PEM interpretation
            interpretation += f"2. PETERSON ELASTIC MODULUS (PEM = {pem:.2f} mmHg):\n"
            if pem != float('inf'):
                if pem > 630:
                    interpretation += "   • HIGH STIFFNESS: Above general population mean+SD\n"
                    interpretation += "   • Risk: Increased cardiovascular risk\n"
                elif pem > 495:
                    interpretation += "   • ELEVATED: Above normotensive population mean+SD\n"
                    interpretation += "   • Consider cardiovascular risk factors\n"
                elif pem > 349:
                    interpretation += "   • NORMAL RANGE: Within normotensive population average\n"
                else:
                    interpretation += "   • LOW STIFFNESS: High arterial elasticity\n"
            else:
                interpretation += "   • Cannot calculate - check measurement validity\n"
            
            interpretation += "\n"
            
            # Beta interpretation
            interpretation += f"3. STIFFNESS PARAMETER (β = {beta:.2f}):\n"
            if beta != float('inf'):
                if beta >= 20.0:
                    interpretation += "   • VERY HIGH RISK: Associated with coronary artery disease\n"
                    interpretation += "   • Recommendation: Urgent cardiovascular evaluation\n"
                elif beta >= 13.0:
                    interpretation += "   • HIGH RISK: Atherosclerosis threshold (80% sensitivity)\n"
                    interpretation += "   • Recommendation: Cardiovascular screening\n"
                elif beta >= 11.7:
                    interpretation += "   • AGE-RELATED: Consistent with 60-69 years normal range\n"
                elif beta >= 8.3:
                    interpretation += "   • NORMAL: Consistent with 40-59 years normal range\n"
                elif beta >= 6.6:
                    interpretation += "   • GOOD ELASTICITY: Consistent with 30-39 years range\n"
                else:
                    interpretation += "   • EXCELLENT ELASTICITY: Young arterial characteristics\n"
            else:
                interpretation += "   • Cannot calculate - check measurement validity\n"
            
            interpretation += "\n"
            
            # DC interpretation
            interpretation += f"4. DISTENSIBILITY (DC = {dc:.2f} × 10⁻⁵ Pa⁻¹):\n"
            if dc != float('inf'):
                if dc >= 4.0:
                    interpretation += "   • NORMAL/HIGH: Consistent with healthy arteries\n"
                    interpretation += "   • Good arterial compliance\n"
                elif dc >= 3.5:
                    interpretation += "   • BORDERLINE: Monitor for changes\n"
                elif dc >= 3.0:
                    interpretation += "   • REDUCED: May indicate arterial disease\n"
                else:
                    interpretation += "   • LOW DISTENSIBILITY: Significant stiffness\n"
                    interpretation += "   • Consider further cardiovascular evaluation\n"
            else:
                interpretation += "   • Cannot calculate - check measurement validity\n"
            
            interpretation += "\n"
            interpretation += "NOTE: Clinical interpretation should be considered alongside patient age, "
            interpretation += "medical history, and other cardiovascular risk factors. "
            interpretation += "These measurements are for research purposes and should not replace "
            interpretation += "professional medical diagnosis."
            
            self.interpretation_text.insert(1.0, interpretation)
            self.interpretation_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"DEBUG: Error updating interpretation: {e}")
    
    def reset_calculations(self):
        """Reset all calculation results"""
        try:
            self.strain_result_label.configure(text="--")
            self.pem_result_label.configure(text="--")
            self.beta_result_label.configure(text="--")
            self.dc_result_label.configure(text="--")
            
            self.interpretation_text.configure(state=tk.NORMAL)
            self.interpretation_text.delete(1.0, tk.END)
            self.interpretation_text.insert(1.0, "No calculations performed yet.\n\nSelect baseline and compressed frames, then click 'Calculate Elasticity Parameters' to begin analysis.")
            self.interpretation_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"DEBUG: Error resetting calculations: {e}")
    
    def export_results(self):
        """Export calculation results to CSV"""
        try:
            if not hasattr(self, 'strain_result_label') or self.strain_result_label.cget("text") == "--":
                messagebox.showwarning("Warning", "No calculations to export. Please calculate elasticity parameters first.")
                return
            
            # Get current results
            strain = self.strain_result_label.cget("text")
            pem = self.pem_result_label.cget("text")
            beta = self.beta_result_label.cget("text")
            dc = self.dc_result_label.cget("text")
            
            # Create export data
            export_data = {
                'Parameter': ['Strain (ε)', 'Peterson Elastic Modulus (PEM)', 'Stiffness Parameter (β)', 'Distensibility (DC)'],
                'Value': [strain, pem, beta, dc],
                'Unit': ['Dimensionless', 'mmHg', 'Dimensionless', '× 10⁻⁵ Pa⁻¹'],
                'Baseline_Frame': [self.baseline_frame_index] * 4,
                'Compressed_Frame': [self.compressed_frame_index] * 4,
                'Baseline_Diameter_mm': [self.baseline_diameter] * 4,
                'Compressed_Diameter_mm': [self.compressed_diameter] * 4,
                'Baseline_Pressure_N': [self.baseline_pressure] * 4,
                'Compressed_Pressure_N': [self.compressed_pressure] * 4,
                'Probe_Area_cm2': [self.probe_contact_area] * 4
            }
            
            df = pd.DataFrame(export_data)
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Elasticity Results"
            )
            
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            
        except Exception as e:
            error_msg = f"Error exporting results: {str(e)}"
            print(f"DEBUG: {error_msg}")
            messagebox.showerror("Export Error", error_msg)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
ELASTICITY CALCULATOR HELP

This tool calculates arterial elasticity parameters from ultrasound diameter measurements and pressure data.

USAGE:
1. Load a subject using the dropdown or Browse Folder button
2. Use the sliders to select baseline (relaxed) and compressed frames
3. Verify the diameter and pressure measurements are displayed correctly
4. Set the probe contact area (default: 1.0 cm²)
5. Click "Calculate Elasticity Parameters" to compute all parameters

PARAMETERS CALCULATED:
• Strain (ε): Relative change in diameter
• Peterson Elastic Modulus (PEM): Arterial stiffness measure
• Stiffness Parameter (β): Dimensionless stiffness index
• Distensibility (DC): Arterial compliance measure

CLINICAL INTERPRETATION:
The tool provides automated clinical interpretation based on established research thresholds and normal ranges from medical literature.

For detailed parameter explanations and clinical significance, refer to the research documentation.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Elasticity Calculator Help")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text)
        text_widget.configure(state=tk.DISABLED)
          # Add scrollbar
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _synchronize_with_timestamps(self, timestamp_df, pressure_df):
        """Synchronize diameter and pressure data using timestamp matching"""
        try:
            if self.diameter_data is None or timestamp_df is None or pressure_df is None:
                return False
            
            # Standardize timestamp formats
            timestamp_df = self._standardize_timestamps(timestamp_df.copy())
            pressure_df = self._standardize_timestamps(pressure_df.copy())
            
            if timestamp_df is None or pressure_df is None:
                return False
            
            # Get frame numbers from diameter data that we need to match
            diameter_frames = self.diameter_data['Frame'].values
            print(f"DEBUG: Need to match {len(diameter_frames)} diameter frames")
            
            # Create mapping from diameter frames to timestamps via timestamp_df
            frame_to_timestamp = {}
            for _, row in timestamp_df.iterrows():
                frame_num = row.get('Frame Number', row.get('frame', None))
                timestamp = row.get('timestamp_normalized', None)
                if frame_num is not None and timestamp is not None:
                    frame_to_timestamp[int(frame_num)] = timestamp
            
            print(f"DEBUG: Created frame-to-timestamp mapping for {len(frame_to_timestamp)} frames")
            
            # Map pressure values to diameter frames
            pressure_values = []
            matched_frames = 0
            
            for frame in diameter_frames:
                frame_int = int(frame)
                if frame_int in frame_to_timestamp:
                    target_timestamp = frame_to_timestamp[frame_int]
                    
                    # Find closest pressure measurement
                    pressure_timestamps = pressure_df['timestamp_normalized'].values
                    closest_idx = np.argmin(np.abs(pressure_timestamps - target_timestamp))
                    pressure_value = pressure_df.iloc[closest_idx]['Sensor Value']
                    pressure_values.append(pressure_value)
                    matched_frames += 1
                else:
                    # Use interpolation for missing frames
                    pressure_values.append(0.0)  # Default value
            
            # Add pressure column to diameter data
            self.diameter_data['pressure'] = pressure_values
            print(f"DEBUG: Successfully matched {matched_frames}/{len(diameter_frames)} frames with pressure data")
            
            # Show sample synchronized data
            print("DEBUG: Sample synchronized data:")
            for i in range(min(5, len(diameter_frames))):
                frame_num = diameter_frames[i]
                diameter = self.diameter_data.iloc[i]['Diameter (mm)']
                pressure = pressure_values[i]
                timestamp = frame_to_timestamp.get(int(frame_num), 'N/A')
                print(f"  Frame {frame_num}: Diameter={diameter:.3f}mm, Pressure={pressure:.3f}N, Timestamp={timestamp}")
            
            return True
            
        except Exception as e:
            print(f"DEBUG: Error in timestamp synchronization: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _standardize_timestamps(self, df):
        """Convert timestamp strings to normalized format for comparison"""
        try:
            timestamp_col = None
            
            # Find timestamp column
            for col in ['Timestamp', 'Timestamp (s)', 'timestamp']:
                if col in df.columns:
                    timestamp_col = col
                    break
            
            if timestamp_col is None:
                print("DEBUG: No timestamp column found")
                return None
            
            # Convert timestamp strings to seconds since start
            timestamps = df[timestamp_col].astype(str)
            normalized_timestamps = []
            
            for ts in timestamps:
                try:
                    # Parse format like "12:31:52.745" or "12-31-52-745"
                    if ':' in ts:
                        # Format: HH:MM:SS.mmm
                        parts = ts.split(':')
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        sec_parts = parts[2].split('.')
                        seconds = int(sec_parts[0])
                        milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
                    else:
                        # Format: HH-MM-SS-mmm
                        parts = ts.split('-')
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = int(parts[2])
                        milliseconds = int(parts[3]) if len(parts) > 3 else 0
                    
                    # Convert to total milliseconds
                    total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
                    normalized_timestamps.append(total_ms)
                    
                except (ValueError, IndexError) as e:
                    print(f"DEBUG: Could not parse timestamp '{ts}': {e}")
                    normalized_timestamps.append(0)
            
            df['timestamp_normalized'] = normalized_timestamps
            
            # Normalize to start from 0
            if normalized_timestamps:
                min_timestamp = min(normalized_timestamps)
                df['timestamp_normalized'] = df['timestamp_normalized'] - min_timestamp
            
            print(f"DEBUG: Normalized {len(normalized_timestamps)} timestamps")
            return df
            
        except Exception as e:
            print(f"DEBUG: Error standardizing timestamps: {e}")
            return None
    
    def _fallback_pressure_mapping(self, subject_name):
        """Fallback method using interpolation when timestamp sync fails"""
        try:
            print("DEBUG: Using fallback interpolation method")
            
            # Look for pressure data in data_uji folder
            data_uji_folder = os.path.join("data_uji", subject_name)
            subject_files = glob.glob(os.path.join(data_uji_folder, f"{subject_name.lower()}.csv"))
            if not subject_files:
                subject_files = glob.glob(os.path.join(data_uji_folder, "subject*.csv"))
                if not subject_files:
                    return
            
            # Load pressure data
            pressure_df = pd.read_csv(subject_files[0])
            pressure_values = pressure_df['Sensor Value'].values
            
            # If we have diameter data with frame numbers, interpolate pressure to match
            if self.diameter_data is not None and 'Frame' in self.diameter_data.columns:
                frame_numbers = self.diameter_data['Frame'].values
                
                # Interpolate pressure values to match frame numbers
                if len(pressure_values) > 0:
                    # Create mapping from frame numbers to pressure indices
                    pressure_indices = np.linspace(0, len(pressure_values)-1, len(frame_numbers), dtype=int)
                    mapped_pressure = pressure_values[pressure_indices]
                      # Add pressure column to diameter data
                    self.diameter_data['pressure'] = mapped_pressure
                    print(f"DEBUG: Fallback mapping - {len(mapped_pressure)} pressure values interpolated")
        
        except Exception as e:
            print(f"DEBUG: Error in fallback pressure mapping: {e}")
    
    def sync_data(self):
        """Synchronize and prepare data for analysis with timestamp support"""
        try:
            if self.diameter_data is None:
                print("DEBUG: No diameter data to sync")
                return
            
            # Copy diameter data to synced_data
            self.synced_data = self.diameter_data.copy()
            print(f"DEBUG: Synced data prepared - {len(self.synced_data)} rows")
            
            # Ensure frame column exists
            if 'Frame' in self.synced_data.columns and 'frame' not in self.synced_data.columns:
                self.synced_data['frame'] = self.synced_data['Frame']
            
            # Load timestamp data if available
            subject_name = self.subject_var.get().split(" [")[0] if self.subject_var.get() else ""
            if subject_name:
                self.load_timestamp_data(subject_name)
            
            # Validate frame range against video bounds
            if self.total_frames > 0:
                frame_min = self.synced_data['frame'].min()
                frame_max = self.synced_data['frame'].max()
                print(f"DEBUG: Frame range: {frame_min} to {frame_max} (video has {self.total_frames} frames)")
                
                # Filter frames within video bounds
                valid_frames = (self.synced_data['frame'] >= 0) & (self.synced_data['frame'] < self.total_frames)
                if valid_frames.any():
                    self.synced_data = self.synced_data[valid_frames]
                    print(f"DEBUG: Filtered to {len(self.synced_data)} frames within video bounds")
            
            # Show sample of synced data
            if len(self.synced_data) > 0:
                print("DEBUG: Sample synced data:")
                for i in range(min(3, len(self.synced_data))):
                    row = self.synced_data.iloc[i]
                    frame_num = row.get('frame', 'N/A')
                    diameter = row.get('diameter', 'N/A')
                    pressure = row.get('pressure', 'N/A')
                    timestamp = row.get('timestamp', 'N/A')
                    print(f"  Frame {frame_num}: Diameter={diameter}, Pressure={pressure}, Time={timestamp}")
            
        except Exception as e:
            print(f"DEBUG: Error syncing data: {e}")
            import traceback
            traceback.print_exc()
    
    def load_timestamp_data(self, subject_name):
        """Load timestamp data and merge with synced data"""
        try:
            timestamp_path = os.path.join("data_uji", subject_name, "timestamps.csv")
            if os.path.exists(timestamp_path):
                timestamp_df = pd.read_csv(timestamp_path)
                print(f"DEBUG: Loaded timestamps: {len(timestamp_df)} rows")
                
                # Standardize column names
                if 'Frame Number' in timestamp_df.columns:
                    timestamp_df['frame'] = timestamp_df['Frame Number']
                if 'Timestamp' in timestamp_df.columns:
                    timestamp_df['timestamp'] = timestamp_df['Timestamp']
                
                # Convert timestamp to seconds from start
                if 'timestamp' in timestamp_df.columns:
                    timestamp_df['time_seconds'] = self.convert_timestamp_to_seconds(timestamp_df['timestamp'])
                
                # Merge with synced data
                if 'frame' in self.synced_data.columns and 'frame' in timestamp_df.columns:
                    original_count = len(self.synced_data)
                    self.synced_data = pd.merge(
                        self.synced_data, 
                        timestamp_df[['frame', 'timestamp', 'time_seconds']], 
                        on='frame', 
                        how='left'
                    )
                    print(f"DEBUG: Merged timestamps - {original_count} -> {len(self.synced_data)} rows")
                    
                    # Show sample with timestamps
                    if len(self.synced_data) > 0 and 'timestamp' in self.synced_data.columns:
                        valid_timestamps = self.synced_data['timestamp'].notna().sum()
                        print(f"DEBUG: {valid_timestamps} rows have valid timestamps")
                        
        except Exception as e:
            print(f"DEBUG: Error loading timestamp data: {e}")
    
    def convert_timestamp_to_seconds(self, timestamps):
        """Convert HH:MM:SS.mmm format to seconds from start"""
        try:
            time_seconds = []
            start_time = None
            
            for ts in timestamps:
                if pd.isna(ts):
                    time_seconds.append(np.nan)
                    continue
                    
                # Parse time string (HH:MM:SS.mmm)
                try:
                    time_parts = str(ts).split(':')
                    if len(time_parts) == 3:
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        seconds_parts = time_parts[2].split('.')
                        seconds = int(seconds_parts[0])
                        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
                        
                        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
                        
                        if start_time is None:
                            start_time = total_seconds
                        
                        time_seconds.append(total_seconds - start_time)
                    else:
                        time_seconds.append(np.nan)
                except:
                    time_seconds.append(np.nan)
            
            return time_seconds
            
        except Exception as e:
            print(f"DEBUG: Error converting timestamps: {e}")
            return [np.nan] * len(timestamps)
    
    def get_x_value_for_frame(self, frame_index, use_timestamp=False):
        """Get X-axis value for a given frame (timestamp or frame number)"""
        try:
            if self.synced_data is None or self.synced_data.empty:
                return None
            
            if use_timestamp and 'time_seconds' in self.synced_data.columns:
                # Find the closest matching frame in synced data
                frame_data = self.synced_data[self.synced_data['frame'] == frame_index]
                if not frame_data.empty:
                    time_value = frame_data['time_seconds'].iloc[0]
                    if not pd.isna(time_value):
                        return time_value
                
                # If exact frame not found, interpolate
                frames = self.synced_data['frame'].values
                times = self.synced_data['time_seconds'].values
                if len(frames) > 1 and frame_index >= frames.min() and frame_index <= frames.max():
                    return np.interp(frame_index, frames, times)
            
            # Default to frame number
            return frame_index
            
        except Exception as e:
            print(f"DEBUG: Error getting X value for frame {frame_index}: {e}")
            return frame_index

def main():
    """Main function to run the Elasticity Calculator"""
    root = tk.Tk()
   
    app = ElasticityCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

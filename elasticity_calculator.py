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
                                status = "✅ Complete" if diameter_files else "⚠️ No Analysis"
                            else:
                                status = "❌ No Results"
                            
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
        
        self.baseline_info_label = ttk.Label(baseline_frame, text="Baseline: Diameter: -- | Pressure: -- N", foreground="blue")
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
            
            # Set initial frame positions
            self.baseline_frame_var.set(0)
            self.compressed_frame_var.set(min(self.total_frames-1, self.total_frames//2))
            self.baseline_frame_index = 0
            self.compressed_frame_index = min(self.total_frames-1, self.total_frames//2)
            
            # Load diameter data
            self.load_diameter_data(subject_name)
            
            # Load pressure data  
            self.load_pressure_data(inference_folder)
            
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
            
            # Prioritize files with pressure data
            pressure_files = [f for f in diameter_files if 'pressure' in f.lower()]
            if pressure_files:
                self.diameter_data = pd.read_csv(pressure_files[0])
                print(f"DEBUG: Loaded diameter data with pressure: {len(self.diameter_data)} rows")
            else:
                # Use the first CSV file found
                self.diameter_data = pd.read_csv(diameter_files[0])
                print(f"DEBUG: Loaded diameter data: {len(self.diameter_data)} rows")
            
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
    
    def load_pressure_data(self, folder):
        """Load pressure data from CSV files"""
        try:
            if not os.path.exists(folder):
                print("DEBUG: Inference folder not found for pressure data")
                return
                
            # Look for CSV files that might contain pressure data
            csv_files = glob.glob(os.path.join(folder, "*.csv"))
            
            for file_path in csv_files:
                df = pd.read_csv(file_path)
                # Check if this file contains pressure data
                if 'pressure' in df.columns or 'Pressure' in df.columns:
                    self.pressure_data = df
                    print(f"DEBUG: Found pressure data in {os.path.basename(file_path)}")
                    return
            
            print("DEBUG: No pressure data found")
            
        except Exception as e:
            print(f"DEBUG: Error loading pressure data: {e}")
            self.pressure_data = None
    
    def sync_data(self):
        """Synchronize diameter and pressure data with frame numbers"""
        try:
            if self.diameter_data is None:
                print("DEBUG: No diameter data to sync")
                return
            
            # Start with diameter data
            self.synced_data = self.diameter_data.copy()
            print(f"DEBUG: Starting sync with {len(self.synced_data)} diameter records")
            
            # Determine frame column
            frame_columns = ['Frame', 'frame', 'frame_number', 'frame_index']
            frame_col = None
            
            for col in frame_columns:
                if col in self.synced_data.columns:
                    frame_col = col
                    break
            
            if frame_col:
                # Use existing frame column
                if frame_col != 'frame':
                    self.synced_data['frame'] = self.synced_data[frame_col]
                    print(f"DEBUG: Used '{frame_col}' column as frame index")
                
                # Keep original frame numbers for reference
                self.synced_data['original_frame'] = self.synced_data['frame']
                
                # Validate frame range
                frame_min = self.synced_data['frame'].min()
                frame_max = self.synced_data['frame'].max()
                print(f"DEBUG: Original frame range: {frame_min} to {frame_max}")
                
                # Ensure frames are within video bounds
                if self.total_frames > 0:
                    print(f"DEBUG: Video has {self.total_frames} frames")
                    valid_frames = (self.synced_data['frame'] >= 0) & (self.synced_data['frame'] < self.total_frames)
                    
                    if valid_frames.any():
                        self.synced_data = self.synced_data[valid_frames]
                        print(f"DEBUG: Keeping original frame numbers (within video range)")
                    else:
                        print("DEBUG: No frames within video range, adjusting...")
                        # Adjust frame numbers to fit video range
                        self.synced_data['frame'] = np.linspace(0, self.total_frames-1, len(self.synced_data), dtype=int)
                
                frame_min = self.synced_data['frame'].min()
                frame_max = self.synced_data['frame'].max()
                print(f"DEBUG: Final frame range: {frame_min} to {frame_max}")
                
            else:
                # Create frame numbers based on data length
                print("DEBUG: No frame column found, creating frame sequence")
                self.synced_data['frame'] = range(len(self.synced_data))
                self.synced_data['original_frame'] = self.synced_data['frame']
            
            print(f"DEBUG: Synced data complete - {len(self.synced_data)} rows")
            print(f"DEBUG: Synced columns: {list(self.synced_data.columns)}")
            
            # Show sample data for debugging
            if len(self.synced_data) > 0:
                print("DEBUG: Sample synced data:")
                for i in range(min(3, len(self.synced_data))):
                    row = self.synced_data.iloc[i]
                    frame_num = row.get('frame', 'N/A')
                    diameter = row.get('diameter', 'N/A')
                    pressure = row.get('pressure', 'N/A')
                    print(f"  Frame {frame_num}: Diameter={diameter}, Pressure={pressure}")
            
        except Exception as e:
            print(f"DEBUG: Error syncing data: {e}")
            import traceback
            traceback.print_exc()
    
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
        """Update the plot with dual vertical lines"""
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
                    
                    # Try to find proper column name for label
                    col_name = 'Diameter (mm)'
                    if 'Diameter (mm)' in self.synced_data.columns:
                        col_name = 'Diameter (mm)'
                    elif 'Diameter' in self.synced_data.columns:
                        col_name = 'Diameter'
                    
                    self.ax.plot(frames, diameters, 'b-', linewidth=2, label=f'{col_name}', alpha=0.8)
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
                    ax2.set_ylabel('Pressure (N)', color='g')
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
            if hasattr(self, 'baseline_frame_index'):
                self.vertical_line1 = self.ax.axvline(x=self.baseline_frame_index, color='blue', 
                                                     linestyle='-', linewidth=2, alpha=0.7, 
                                                     label=f'Baseline Frame {self.baseline_frame_index}')
            
            if hasattr(self, 'compressed_frame_index'):
                self.vertical_line2 = self.ax.axvline(x=self.compressed_frame_index, color='red', 
                                                     linestyle='-', linewidth=2, alpha=0.7, 
                                                     label=f'Compressed Frame {self.compressed_frame_index}')
            
            # Set axis limits - Always start from 0 and show all data
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
            print(f"DEBUG: Error in update_plot: {e}")
            self.ax.text(0.5, 0.5, f'Error plotting data:\n{str(e)}', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=10, color='red')
        
        # Set labels and title
        self.ax.set_xlabel('Frame Number')
        self.ax.set_title('Diameter and Pressure vs Frame - Elasticity Analysis')
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


def main():
    """Main function to run the Elasticity Calculator"""
    root = tk.Tk()
    app = ElasticityCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

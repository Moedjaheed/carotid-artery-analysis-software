"""
Launcher Script untuk Segmentasi Karotis - Dark Mode Version
Script untuk menjalankan semua komponen dengan mudah
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
from theme_manager import ThemeManager

class SegmentationLauncher:
    """Launcher GUI dengan sistem tab seperti browser dan dark mode"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Carotid Segmentation Suite")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        print("DEBUG: Initializing Carotid Segmentation Launcher...")
        print(f"DEBUG: Working directory: {os.getcwd()}")
        print(f"DEBUG: Python executable: {sys.executable}")
        
        # Initialize variables
        self.status_var = tk.StringVar(value="Ready")
        
        self.setup_tabbed_ui()
        
        # Apply initial theme
        self.apply_current_theme()
    
    def setup_tabbed_ui(self):
        """Setup tabbed user interface like a browser"""
        print("DEBUG: Setting up tabbed user interface...")
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header with title and status
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🩺 Carotid Segmentation Suite", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Theme toggle button in header
        theme_toggle_btn = ttk.Button(header_frame, text="🌓 Theme", 
                                     command=self.toggle_theme_quick)
        theme_toggle_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status bar
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        ttk.Label(status_frame, text="Status:", font=("Arial", 9)).pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                font=("Arial", 9, "italic"), foreground="blue")
        status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Create notebook (tab container)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_home_tab()
        self.create_inference_tab()
        self.create_analytics_tab()
        self.create_tools_tab()
        self.create_settings_tab()
        
        print("DEBUG: Tabbed user interface setup completed")
    
    def create_home_tab(self):
        """Create home/dashboard tab"""
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="🏠 Home")
          # Welcome section
        welcome_frame = ttk.LabelFrame(home_frame, text="Welcome", padding=15)
        welcome_frame.pack(fill=tk.X, padx=10, pady=5)
        
        welcome_text = """Welcome to Carotid Segmentation Analysis Suite!

This application provides comprehensive tools for analyzing carotid artery diameter 
measurements using advanced AI segmentation and data visualization.

🆕 NEW FEATURES:
• Multiple Subject Selection: Process multiple subjects simultaneously using checkboxes
• Model Selection: Choose between different AI models using radiobuttons  
• Enhanced Processing: Integrated pressure data analysis with correlation plots
• Batch Processing: Efficient processing of multiple subjects with progress monitoring"""
        
        ttk.Label(welcome_frame, text=welcome_text, font=("Arial", 11), 
                 justify=tk.LEFT, wraplength=700).pack(anchor=tk.W)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(home_frame, text="Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack(fill=tk.X)
        
        # Row 1
        ttk.Button(actions_grid, text="🎯 Enhanced Inference", 
                  command=self.run_enhanced_inference, width=20).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(actions_grid, text="📊 Data Viewer", 
                  command=self.run_data_viewer, width=20).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(actions_grid, text="📈 Analytics", 
                  command=self.run_advanced_analytics, width=20).grid(row=0, column=2, padx=5, pady=5)
        
        # Configure grid weights
        actions_grid.columnconfigure(0, weight=1)
        actions_grid.columnconfigure(1, weight=1)
        actions_grid.columnconfigure(2, weight=1)
    
    def create_inference_tab(self):
        """Create inference processing tab"""
        inference_frame = ttk.Frame(self.notebook)
        self.notebook.add(inference_frame, text="🎯 Inference")
          # Enhanced Inference section
        enhanced_frame = ttk.LabelFrame(inference_frame, text="Enhanced Inference", padding=15)
        enhanced_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(enhanced_frame, text="Advanced AI inference with multiple model and subject selection", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(enhanced_frame, text="✨ New Features: Multiple subject selection (checkboxes) + Model selection (radiobuttons)", 
                 font=("Arial", 9), foreground="darkgreen").pack(anchor=tk.W, pady=(0, 10))
        
        inference_buttons = ttk.Frame(enhanced_frame)
        inference_buttons.pack(fill=tk.X)
        
        ttk.Button(inference_buttons, text="🎯 Enhanced Inference (Multiple Subjects + Model Selection)", 
                  command=self.run_enhanced_inference, width=50).pack(pady=2, fill=tk.X)
        ttk.Button(inference_buttons, text="📋 Single Subject Inference (Legacy)", 
                  command=self.run_single_inference, width=50).pack(pady=2, fill=tk.X)
    
    def create_analytics_tab(self):
        """Create analytics and visualization tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Data Viewer section
        viewer_frame = ttk.LabelFrame(analytics_frame, text="Data Visualization", padding=15)
        viewer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(viewer_frame, text="Interactive data visualization and analysis tools", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(viewer_frame, text="📈 Enhanced Data Viewer", 
                  command=self.run_data_viewer, width=30).pack(fill=tk.X)
        
        # Advanced Analytics section
        advanced_frame = ttk.LabelFrame(analytics_frame, text="Advanced Analytics", padding=15)
        advanced_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(advanced_frame, text="Comprehensive statistical analysis and reporting", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(advanced_frame, text="📊 Advanced Analytics Dashboard", 
                  command=self.run_advanced_analytics, width=30).pack(fill=tk.X)
    
    def create_tools_tab(self):
        """Create tools and utilities tab"""
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="🔧 Tools")
        
        # System tools
        system_frame = ttk.LabelFrame(tools_frame, text="System Tools", padding=15)
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tools_grid = ttk.Frame(system_frame)
        tools_grid.pack(fill=tk.X)
        
        ttk.Button(tools_grid, text="🔍 Check Dependencies", 
                  command=self.check_dependencies).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(tools_grid, text="📂 Open Data Folder", 
                  command=self.open_data_folder).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tools_grid.columnconfigure(0, weight=1)
        tools_grid.columnconfigure(1, weight=1)
    
    def create_settings_tab(self):
        """Create settings tab with theme controls"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Create scrollable frame
        canvas = tk.Canvas(settings_frame)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Theme Settings Section
        theme_section = ttk.LabelFrame(scrollable_frame, text="🎨 Appearance Settings", 
                                     padding=10)
        theme_section.pack(fill="x", padx=10, pady=5)
        
        # Current theme display
        current_theme_frame = ttk.Frame(theme_section)
        current_theme_frame.pack(fill="x", pady=5)
        
        ttk.Label(current_theme_frame, text="Current Theme:", 
                 font=("Arial", 9, "bold")).pack(side="left")
        
        self.current_theme_label = ttk.Label(current_theme_frame, 
                                           text=self.theme_manager.current_theme.title(),
                                           font=("Arial", 9))
        self.current_theme_label.pack(side="left", padx=10)
        
        # Theme Selection
        theme_selection_frame = ttk.Frame(theme_section)
        theme_selection_frame.pack(fill="x", pady=5)
        
        ttk.Label(theme_selection_frame, text="Select Theme:", 
                 font=("Arial", 9)).pack(side="left")
        
        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        
        light_radio = ttk.Radiobutton(theme_selection_frame, text="☀️ Light Mode", 
                                    variable=self.theme_var, value="light",
                                    command=self.change_theme)
        light_radio.pack(side="left", padx=10)
        
        dark_radio = ttk.Radiobutton(theme_selection_frame, text="🌙 Dark Mode", 
                                   variable=self.theme_var, value="dark",
                                   command=self.change_theme)
        dark_radio.pack(side="left", padx=10)
        
        # Theme Toggle Button
        theme_buttons_frame = ttk.Frame(theme_section)
        theme_buttons_frame.pack(fill="x", pady=10)
        
        toggle_btn = ttk.Button(theme_buttons_frame, text="🔄 Toggle Theme", 
                               command=self.toggle_theme_with_update)
        toggle_btn.pack(side="left", padx=5)
        
        reset_btn = ttk.Button(theme_buttons_frame, text="🔄 Reset to Light", 
                              command=self.reset_theme)
        reset_btn.pack(side="left", padx=5)
    
    def toggle_theme_quick(self):
        """Quick theme toggle from header button"""
        new_theme = self.theme_manager.switch_theme()
        self.apply_current_theme()
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.config(text=new_theme.title())
        if hasattr(self, 'theme_var'):
            self.theme_var.set(new_theme)
        self.status_var.set(f"Theme changed to {new_theme.title()} Mode")
    
    def apply_current_theme(self):
        """Apply current theme to all widgets"""
        # Configure ttk styles first
        self.theme_manager.configure_ttk_style()
        
        # Apply theme to root and all widgets
        self.theme_manager.apply_theme_recursive(self.root)
        
        # Update matplotlib plots if they exist
        self.update_matplotlib_theme()
    
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
        """Change theme based on radio button selection"""
        selected_theme = self.theme_var.get()
        self.theme_manager.set_theme(selected_theme)
        self.apply_current_theme()
        self.current_theme_label.config(text=selected_theme.title())
        self.status_var.set(f"Theme changed to {selected_theme.title()} Mode")
    
    def toggle_theme_with_update(self):
        """Toggle theme and update UI elements"""
        new_theme = self.theme_manager.switch_theme()
        self.theme_var.set(new_theme)
        self.apply_current_theme()
        self.current_theme_label.config(text=new_theme.title())
        self.status_var.set(f"Theme toggled to {new_theme.title()} Mode")
    
    def reset_theme(self):
        """Reset theme to light mode"""
        self.theme_manager.set_theme("light")
        self.theme_var.set("light")
        self.apply_current_theme()
        self.current_theme_label.config(text="Light")
        self.status_var.set("Theme reset to Light Mode")
    
    # Application launch methods
    def run_enhanced_inference(self):
        """Launch enhanced inference GUI with multiple subjects and model selection"""
        print("DEBUG: Starting Enhanced Inference GUI...")
        self.status_var.set("Starting Enhanced Inference GUI...")
        
        try:
            # Check if enhanced inference GUI exists
            if os.path.exists("enhanced_inference_gui.py"):
                subprocess.Popen([sys.executable, "enhanced_inference_gui.py"], 
                               cwd=os.getcwd())
                self.status_var.set("Enhanced Inference GUI launched")
                print("DEBUG: Enhanced Inference GUI launched successfully")
            else:
                # Fallback to original video_inference.py
                print("DEBUG: Enhanced GUI not found, using fallback...")
                subprocess.Popen([sys.executable, "video_inference.py"], 
                               cwd=os.getcwd())
                self.status_var.set("Enhanced Inference launched (fallback mode)")
        except Exception as e:
            print(f"DEBUG: Error launching enhanced inference: {e}")
            self.status_var.set("Error launching enhanced inference")
            messagebox.showerror("Error", f"Failed to launch enhanced inference: {str(e)}")
    
    def run_single_inference(self):
        """Launch single subject inference"""
        print("DEBUG: Starting Single Subject Inference...")
        self.status_var.set("Starting Single Subject Inference...")
        
        try:
            subprocess.Popen([sys.executable, "main.py"], cwd=os.getcwd())
            self.status_var.set("Single inference launched")
        except Exception as e:
            print(f"DEBUG: Error launching single inference: {e}")
            self.status_var.set("Error launching single inference")
            messagebox.showerror("Error", f"Failed to launch single inference: {str(e)}")
    
    def run_data_viewer(self):
        """Launch data viewer"""
        print("DEBUG: Starting Data Viewer...")
        self.status_var.set("Starting Data Viewer...")
        
        try:
            subprocess.Popen([sys.executable, "data_viewer.py"], cwd=os.getcwd())
            self.status_var.set("Data Viewer launched")
        except Exception as e:
            print(f"DEBUG: Error launching data viewer: {e}")
            self.status_var.set("Error launching data viewer")
            messagebox.showerror("Error", f"Failed to launch data viewer: {str(e)}")
    
    def run_advanced_analytics(self):
        """Launch advanced analytics"""
        print("DEBUG: Starting Advanced Analytics...")
        self.status_var.set("Starting Advanced Analytics...")
        
        try:
            subprocess.Popen([sys.executable, "advanced_analytics.py"], cwd=os.getcwd())
            self.status_var.set("Advanced Analytics launched")
        except Exception as e:
            print(f"DEBUG: Error launching advanced analytics: {e}")
            self.status_var.set("Error launching advanced analytics")
            messagebox.showerror("Error", f"Failed to launch advanced analytics: {str(e)}")
    
    def check_dependencies(self):
        """Check system dependencies"""
        print("DEBUG: Checking dependencies...")
        self.status_var.set("Checking dependencies...")
        
        try:
            # Create dependency check window
            dep_window = tk.Toplevel(self.root)
            dep_window.title("System Dependencies Check")
            dep_window.geometry("600x400")
            dep_window.transient(self.root)
            dep_window.grab_set()
            
            # Apply current theme to new window
            self.theme_manager.apply_theme_recursive(dep_window)
            
            text_area = tk.Text(dep_window, wrap=tk.WORD, padx=10, pady=10)
            text_area.pack(fill=tk.BOTH, expand=True)
            
            # Check dependencies
            deps_status = "System Dependencies Check\n" + "="*50 + "\n\n"
            
            # Check Python version
            deps_status += f"Python Version: {sys.version}\n"
            
            # Check key modules
            modules = ['cv2', 'pandas', 'numpy', 'matplotlib', 'tkinter', 'PIL']
            for module in modules:
                try:
                    __import__(module)
                    deps_status += f"✓ {module}: Available\n"
                except ImportError:
                    deps_status += f"✗ {module}: Missing\n"
            
            deps_status += f"\nWorking Directory: {os.getcwd()}\n"
            deps_status += f"Current Theme: {self.theme_manager.current_theme.title()}\n"
            
            text_area.insert(tk.END, deps_status)
            text_area.config(state=tk.DISABLED)
            
            self.status_var.set("Dependencies check completed")
            
        except Exception as e:
            print(f"DEBUG: Error checking dependencies: {e}")
            self.status_var.set("Error checking dependencies")
            messagebox.showerror("Error", f"Failed to check dependencies: {str(e)}")
    
    def open_data_folder(self):
        """Open data folder in file explorer"""
        try:
            data_path = os.path.join(os.getcwd(), "data_uji")
            if os.path.exists(data_path):
                if sys.platform == "win32":
                    os.startfile(data_path)
                else:
                    subprocess.run(["xdg-open", data_path])
                self.status_var.set("Data folder opened")
            else:
                messagebox.showwarning("Warning", "Data folder not found")
                self.status_var.set("Data folder not found")
        except Exception as e:
            print(f"DEBUG: Error opening data folder: {e}")
            messagebox.showerror("Error", f"Failed to open data folder: {str(e)}")

def main():
    """Main function"""
    print("DEBUG: Starting main function...")
    print(f"DEBUG: Python version: {sys.version}")
    print(f"DEBUG: Current working directory: {os.getcwd()}")
    print(f"DEBUG: Script location: {os.path.abspath(__file__)}")
    
    try:
        root = tk.Tk()
        print("DEBUG: Tkinter root window created")
        
        app = SegmentationLauncher(root)
        print("DEBUG: SegmentationLauncher initialized")
        
        print("DEBUG: Starting main loop...")
        root.mainloop()
        print("DEBUG: Main loop ended")
        
    except Exception as e:
        print(f"DEBUG: Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main()

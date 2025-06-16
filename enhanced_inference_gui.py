"""
Enhanced Inference GUI untuk Multiple Subject Selection
Dengan checkbox untuk memilih subjects dan radiobutton untuk memilih model
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import glob
from datetime import datetime
import json

class EnhancedInferenceGUI:
    """GUI untuk Enhanced Inference dengan Multiple Subject Selection"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Inference - Multiple Subject & Model Selection")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Variables
        self.selected_subjects = {}  # Dictionary untuk menyimpan checkbox states
        self.selected_model = tk.StringVar()
        self.use_pressure = tk.BooleanVar(value=True)
        self.processing = False
        self.progress_var = tk.StringVar(value="Ready")
        
        # Initialize GUI
        self.setup_gui()
        self.scan_subjects()
        self.scan_models()
        
    def setup_gui(self):
        """Setup GUI components"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎯 Enhanced Inference Suite", 
                              font=("Arial", 16, "bold"), fg="darkblue")
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Subject Selection Tab
        self.create_subject_tab(notebook)
        
        # Model Selection Tab  
        self.create_model_tab(notebook)
        
        # Processing Options Tab
        self.create_options_tab(notebook)
        
        # Progress Tab
        self.create_progress_tab(notebook)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
    def create_subject_tab(self, notebook):
        """Create subject selection tab with checkboxes"""
        subject_frame = ttk.Frame(notebook)
        notebook.add(subject_frame, text="📋 Subject Selection")
        
        # Header
        header_frame = tk.Frame(subject_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, text="Select Subjects for Processing", 
                font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Select/Deselect all buttons
        button_frame = tk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        tk.Button(button_frame, text="Select All", command=self.select_all_subjects,
                 bg="lightgreen", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Deselect All", command=self.deselect_all_subjects,
                 bg="lightcoral", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.scan_subjects,
                 bg="lightblue", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        
        # Subject list frame with scrollbar
        list_frame = tk.Frame(subject_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(list_frame, bg="white")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.subject_scrollable_frame = tk.Frame(canvas, bg="white")
        
        self.subject_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.subject_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status info
        self.subject_status_label = tk.Label(subject_frame, 
                                           text="No subjects scanned yet", 
                                           font=("Arial", 10), fg="gray")
        self.subject_status_label.pack(pady=5)
        
    def create_model_tab(self, notebook):
        """Create model selection tab with radiobuttons"""
        model_frame = ttk.Frame(notebook)
        notebook.add(model_frame, text="🤖 Model Selection")
        
        # Header
        header_frame = tk.Frame(model_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, text="Select AI Model for Processing", 
                font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        tk.Button(header_frame, text="Refresh Models", command=self.scan_models,
                 bg="lightblue", relief=tk.RAISED).pack(side=tk.RIGHT)
        
        # Model list frame
        self.model_list_frame = tk.Frame(model_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.model_list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # Custom model selection
        custom_frame = tk.LabelFrame(model_frame, text="Custom Model", padx=10, pady=10)
        custom_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.custom_model_path = tk.StringVar()
        tk.Entry(custom_frame, textvariable=self.custom_model_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(custom_frame, text="Browse", command=self.browse_custom_model).pack(side=tk.LEFT, padx=5)
        
        # Model status
        self.model_status_label = tk.Label(model_frame, 
                                         text="No models scanned yet", 
                                         font=("Arial", 10), fg="gray")
        self.model_status_label.pack(pady=5)
        
    def create_options_tab(self, notebook):
        """Create processing options tab"""
        options_frame = ttk.Frame(notebook)
        notebook.add(options_frame, text="⚙️ Processing Options")
        
        # Processing options
        processing_frame = tk.LabelFrame(options_frame, text="Processing Settings", 
                                       padx=20, pady=15)
        processing_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # Enhanced processing option
        pressure_frame = tk.Frame(processing_frame)
        pressure_frame.pack(fill=tk.X, pady=5)
        
        tk.Checkbutton(pressure_frame, text="Enable Enhanced Processing with Pressure Integration",
                      variable=self.use_pressure, font=("Arial", 11)).pack(side=tk.LEFT)
        
        tk.Label(pressure_frame, text="ℹ️", font=("Arial", 12), fg="blue").pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = """Enhanced Processing includes:
• Pressure data integration from subject CSV files
• Timestamp synchronization
• Correlation analysis between diameter and pressure
• Advanced plotting with dual-axis visualization
• Statistical analysis and reporting"""
        
        info_label = tk.Label(processing_frame, text=info_text, 
                             font=("Arial", 9), justify=tk.LEFT, 
                             wraplength=500, fg="darkgreen")
        info_label.pack(pady=10, anchor=tk.W)
        
        # Output options
        output_frame = tk.LabelFrame(options_frame, text="Output Settings", 
                                   padx=20, pady=15)
        output_frame.pack(fill=tk.X, pady=20, padx=20)
        
        self.save_individual = tk.BooleanVar(value=True)
        self.save_combined = tk.BooleanVar(value=False)
        
        tk.Checkbutton(output_frame, text="Save individual subject results",
                      variable=self.save_individual, font=("Arial", 11)).pack(anchor=tk.W)
        tk.Checkbutton(output_frame, text="Create combined analysis report",
                      variable=self.save_combined, font=("Arial", 11)).pack(anchor=tk.W)
        
    def create_progress_tab(self, notebook):
        """Create progress monitoring tab"""
        progress_frame = ttk.Frame(notebook)
        notebook.add(progress_frame, text="📊 Progress")
        
        # Progress display
        progress_container = tk.Frame(progress_frame)
        progress_container.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)
        
        tk.Label(progress_container, text="Processing Status", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(progress_container, textvariable=self.progress_var,
                                   font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_container, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Log area
        log_frame = tk.LabelFrame(progress_container, text="Processing Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text area with scrollbar
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, height=15, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
    def create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Left side buttons
        left_buttons = tk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="💾 Save Configuration", 
                 command=self.save_config, bg="lightblue").pack(side=tk.LEFT, padx=5)
        tk.Button(left_buttons, text="📂 Load Configuration", 
                 command=self.load_config, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        
        # Right side buttons
        right_buttons = tk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        self.start_button = tk.Button(right_buttons, text="🚀 Start Processing", 
                                     command=self.start_processing, 
                                     bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(right_buttons, text="⏹️ Stop", 
                                    command=self.stop_processing, 
                                    bg="red", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(right_buttons, text="❌ Close", 
                 command=self.root.quit, bg="gray").pack(side=tk.LEFT, padx=5)
        
    def scan_subjects(self):
        """Scan for available subjects in data_uji folder"""
        self.log_message("Scanning for subjects...")
        
        # Clear existing checkboxes
        for widget in self.subject_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.selected_subjects.clear()
        
        if not os.path.exists("data_uji"):
            self.subject_status_label.config(text="❌ data_uji folder not found!")
            return
            
        subjects = []
        for item in os.listdir("data_uji"):
            subject_path = os.path.join("data_uji", item)
            if os.path.isdir(subject_path):
                # Check if subject has required files
                video_file = os.path.join(subject_path, f"{item}.mp4")
                has_video = os.path.exists(video_file)
                
                # Check for pressure files
                pressure_patterns = [
                    os.path.join(subject_path, f"subject{item[-1]}.csv"),
                    os.path.join(subject_path, f"{item.lower()}.csv"),
                    os.path.join(subject_path, "pressure.csv")
                ]
                has_pressure = any(os.path.exists(p) for p in pressure_patterns)
                
                # Check for timestamps
                timestamp_file = os.path.join(subject_path, "timestamps.csv")
                has_timestamps = os.path.exists(timestamp_file)
                
                subjects.append({
                    'name': item,
                    'has_video': has_video,
                    'has_pressure': has_pressure,
                    'has_timestamps': has_timestamps,
                    'path': subject_path
                })
        
        # Create checkboxes for each subject
        for i, subject in enumerate(subjects):
            subject_frame = tk.Frame(self.subject_scrollable_frame, bg="white", relief=tk.RIDGE, bd=1)
            subject_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Checkbox variable
            var = tk.BooleanVar()
            self.selected_subjects[subject['name']] = var
            
            # Main checkbox and label
            main_frame = tk.Frame(subject_frame, bg="white")
            main_frame.pack(fill=tk.X, padx=10, pady=5)
            
            checkbox = tk.Checkbutton(main_frame, text=subject['name'], 
                                     variable=var, font=("Arial", 11, "bold"), 
                                     bg="white")
            checkbox.pack(side=tk.LEFT)
            
            # Status indicators
            status_frame = tk.Frame(main_frame, bg="white")
            status_frame.pack(side=tk.RIGHT)
            
            if subject['has_video']:
                tk.Label(status_frame, text="🎥", font=("Arial", 12)).pack(side=tk.LEFT)
            else:
                tk.Label(status_frame, text="❌🎥", font=("Arial", 12), fg="red").pack(side=tk.LEFT)
                
            if subject['has_pressure']:
                tk.Label(status_frame, text="📊", font=("Arial", 12)).pack(side=tk.LEFT)
            else:
                tk.Label(status_frame, text="❌📊", font=("Arial", 12), fg="orange").pack(side=tk.LEFT)
                
            if subject['has_timestamps']:
                tk.Label(status_frame, text="⏰", font=("Arial", 12)).pack(side=tk.LEFT)
            else:
                tk.Label(status_frame, text="❌⏰", font=("Arial", 12), fg="orange").pack(side=tk.LEFT)
            
            # Status text
            status_text = "Ready" if subject['has_video'] else "Missing video file"
            if not subject['has_pressure'] or not subject['has_timestamps']:
                status_text += " (Enhanced processing not available)"
                
            tk.Label(subject_frame, text=f"Status: {status_text}", 
                    font=("Arial", 9), fg="gray", bg="white").pack(padx=10, pady=(0, 5))
        
        # Update status
        total_subjects = len(subjects)
        ready_subjects = sum(1 for s in subjects if s['has_video'])
        enhanced_ready = sum(1 for s in subjects if s['has_video'] and s['has_pressure'] and s['has_timestamps'])
        
        status_text = f"Found {total_subjects} subjects | {ready_subjects} ready for processing | {enhanced_ready} ready for enhanced processing"
        self.subject_status_label.config(text=status_text, fg="green" if ready_subjects > 0 else "red")
        
        self.log_message(f"Subject scan completed: {status_text}")
        
    def scan_models(self):
        """Scan for available model files"""
        self.log_message("Scanning for model files...")
        
        # Clear existing radiobuttons
        for widget in self.model_list_frame.winfo_children():
            widget.destroy()
            
        # Look for .pth files in current directory
        model_files = glob.glob("*.pth")
        
        if not model_files:
            tk.Label(self.model_list_frame, text="❌ No .pth model files found in current directory",
                    font=("Arial", 11), fg="red", bg="white").pack(pady=20)
            self.model_status_label.config(text="No models found", fg="red")
            return
        
        # Set default model if not set
        if not self.selected_model.get():
            self.selected_model.set(model_files[0])
        
        # Create radiobuttons for each model
        for model_file in model_files:
            model_frame = tk.Frame(self.model_list_frame, bg="white")
            model_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Radiobutton
            rb = tk.Radiobutton(model_frame, text=model_file, 
                               variable=self.selected_model, value=model_file,
                               font=("Arial", 11), bg="white")
            rb.pack(side=tk.LEFT)
            
            # Model info
            try:
                stat = os.stat(model_file)
                size_mb = stat.st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                info_text = f"Size: {size_mb:.1f} MB | Modified: {mod_time}"
                tk.Label(model_frame, text=info_text, font=("Arial", 9), 
                        fg="gray", bg="white").pack(side=tk.RIGHT)
            except:
                pass
        
        # Update status
        self.model_status_label.config(text=f"Found {len(model_files)} model files", fg="green")
        self.log_message(f"Model scan completed: Found {len(model_files)} models")
        
    def select_all_subjects(self):
        """Select all subjects"""
        for var in self.selected_subjects.values():
            var.set(True)
        self.log_message("All subjects selected")
        
    def deselect_all_subjects(self):
        """Deselect all subjects"""
        for var in self.selected_subjects.values():
            var.set(False)
        self.log_message("All subjects deselected")
        
    def browse_custom_model(self):
        """Browse for custom model file"""
        filename = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("PyTorch Models", "*.pth"), ("All Files", "*.*")]
        )
        if filename:
            self.custom_model_path.set(filename)
            self.selected_model.set("custom")
            self.log_message(f"Custom model selected: {filename}")
            
    def save_config(self):
        """Save current configuration"""
        config = {
            'selected_subjects': {name: var.get() for name, var in self.selected_subjects.items()},
            'selected_model': self.selected_model.get(),
            'custom_model_path': self.custom_model_path.get(),
            'use_pressure': self.use_pressure.get(),
            'save_individual': self.save_individual.get(),
            'save_combined': self.save_combined.get()
        }
        
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                self.log_message(f"Configuration saved: {filename}")
                messagebox.showinfo("Success", "Configuration saved successfully!")
            except Exception as e:
                self.log_message(f"Error saving configuration: {e}")
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                
    def load_config(self):
        """Load configuration"""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Apply configuration
                for name, selected in config.get('selected_subjects', {}).items():
                    if name in self.selected_subjects:
                        self.selected_subjects[name].set(selected)
                
                if 'selected_model' in config:
                    self.selected_model.set(config['selected_model'])
                if 'custom_model_path' in config:
                    self.custom_model_path.set(config['custom_model_path'])
                if 'use_pressure' in config:
                    self.use_pressure.set(config['use_pressure'])
                if 'save_individual' in config:
                    self.save_individual.set(config['save_individual'])
                if 'save_combined' in config:
                    self.save_combined.set(config['save_combined'])
                
                self.log_message(f"Configuration loaded: {filename}")
                messagebox.showinfo("Success", "Configuration loaded successfully!")
                
            except Exception as e:
                self.log_message(f"Error loading configuration: {e}")
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def start_processing(self):
        """Start the inference processing"""
        # Validate selections
        selected_subjects_list = [name for name, var in self.selected_subjects.items() if var.get()]
        
        if not selected_subjects_list:
            messagebox.showwarning("Warning", "Please select at least one subject to process.")
            return
            
        if not self.selected_model.get():
            messagebox.showwarning("Warning", "Please select a model to use.")
            return
            
        # Get model path
        if self.selected_model.get() == "custom":
            model_path = self.custom_model_path.get()
            if not model_path or not os.path.exists(model_path):
                messagebox.showwarning("Warning", "Please specify a valid custom model path.")
                return
        else:
            model_path = self.selected_model.get()
            if not os.path.exists(model_path):
                messagebox.showerror("Error", f"Model file not found: {model_path}")
                return
        
        # Start processing in separate thread
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        
        # Run processing in thread
        processing_thread = threading.Thread(
            target=self.run_processing,
            args=(selected_subjects_list, model_path)
        )
        processing_thread.daemon = True
        processing_thread.start()
        
    def run_processing(self, subjects, model_path):
        """Run the actual processing"""
        try:
            total_subjects = len(subjects)
            completed = 0
            
            self.update_progress(f"Starting processing of {total_subjects} subjects...")
            
            for subject in subjects:
                if not self.processing:  # Check if stopped
                    break
                    
                self.update_progress(f"Processing {subject} ({completed + 1}/{total_subjects})...")
                
                # Build command
                cmd = [sys.executable, "video_inference.py", "--subject", subject]
                
                if self.use_pressure.get():
                    cmd.append("--use_pressure")
                
                # Run inference
                try:
                    # Set environment variable
                    env = os.environ.copy()
                    env['PYTHONPATH'] = os.getcwd()
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, 
                                          cwd=os.getcwd(), env=env, timeout=3600)  # 1 hour timeout
                    
                    if result.returncode == 0:
                        self.log_message(f"✅ {subject}: Processing completed successfully")
                        completed += 1
                    else:
                        self.log_message(f"❌ {subject}: Processing failed")
                        self.log_message(f"Error output: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_message(f"⏰ {subject}: Processing timed out")
                except Exception as e:
                    self.log_message(f"❌ {subject}: Exception occurred: {e}")
                
                # Update progress
                progress_pct = ((completed) / total_subjects) * 100
                self.update_progress(f"Completed {completed}/{total_subjects} subjects ({progress_pct:.1f}%)")
            
            # Final status
            if self.processing:  # Not stopped by user
                self.update_progress(f"✅ Processing completed! {completed}/{total_subjects} subjects processed successfully")
                if completed == total_subjects:
                    messagebox.showinfo("Success", f"All {total_subjects} subjects processed successfully!")
                else:
                    messagebox.showwarning("Partial Success", 
                                         f"Processed {completed} out of {total_subjects} subjects. Check log for details.")
            else:
                self.update_progress("⏹️ Processing stopped by user")
                
        except Exception as e:
            self.log_message(f"❌ Critical error during processing: {e}")
            self.update_progress("❌ Processing failed due to critical error")
            messagebox.showerror("Error", f"Processing failed: {e}")
        finally:
            # Reset UI
            self.processing = False
            self.progress_bar.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_processing(self):
        """Stop the processing"""
        self.processing = False
        self.update_progress("Stopping processing...")
        self.log_message("🛑 Stop requested by user")
        
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.log_message(message)
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Update log text (from main thread)
        self.root.after(0, lambda: self._append_log(log_entry))
        
    def _append_log(self, text):
        """Append text to log (must be called from main thread)"""
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)


def main():
    """Main function"""
    root = tk.Tk()
    app = EnhancedInferenceGUI(root)
    
    # Handle window close
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("Quit", "Processing is running. Do you want to stop and quit?"):
                app.processing = False
                root.quit()
        else:
            root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

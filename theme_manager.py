# theme_manager.py
import tkinter as tk
from tkinter import ttk
import json
import os

class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.config_file = "theme_config.json"
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "button_active_bg": "#e0e0e0",
                "frame_bg": "#f5f5f5",
                "text_bg": "#ffffff",
                "text_fg": "#000000",
                "accent": "#0078d4",
                "secondary": "#6c757d",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "border": "#cccccc",
                "hover": "#e8f4fd",
                "menu_bg": "#ffffff",
                "menu_fg": "#000000",
                "tab_bg": "#f0f0f0",
                "tab_fg": "#000000",
                "tab_active_bg": "#ffffff",
                "tab_active_fg": "#000000"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "select_bg": "#404040",
                "select_fg": "#ffffff",
                "entry_bg": "#404040",
                "entry_fg": "#ffffff",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
                "button_active_bg": "#555555",
                "frame_bg": "#353535",
                "text_bg": "#2b2b2b",
                "text_fg": "#ffffff",
                "accent": "#4CAF50",
                "secondary": "#9e9e9e",
                "success": "#4CAF50",
                "warning": "#ff9800",
                "danger": "#f44336",
                "border": "#555555",
                "hover": "#3d3d3d",
                "menu_bg": "#2b2b2b",
                "menu_fg": "#ffffff",
                "tab_bg": "#404040",
                "tab_fg": "#ffffff",
                "tab_active_bg": "#2b2b2b",
                "tab_active_fg": "#ffffff"
            }
        }
        self.load_theme_config()
    
    def load_theme_config(self):
        """Load theme configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("current_theme", "light")
        except Exception as e:
            print(f"Error loading theme config: {e}")
            self.current_theme = "light"
    
    def save_theme_config(self):
        """Save current theme configuration to file"""
        try:
            config = {"current_theme": self.current_theme}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving theme config: {e}")
    
    def get_theme(self, theme_name=None):
        """Get theme colors dictionary"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["light"])
    
    def get_theme_colors(self, theme_name=None):
        """Get theme colors dictionary (alias for get_theme)"""
        return self.get_theme(theme_name)
    
    def switch_theme(self):
        """Switch between light and dark theme"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_theme_config()
        return self.current_theme
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.save_theme_config()
            return True
        return False
    
    def apply_theme_to_widget(self, widget, widget_type="default"):
        """Apply theme to a specific widget"""
        theme = self.get_theme()
        
        try:
            if isinstance(widget, (tk.Tk, tk.Toplevel)):
                widget.configure(bg=theme["bg"])
            
            elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=theme["frame_bg"])
                if hasattr(widget, 'configure'):
                    try:
                        widget.configure(fg=theme["fg"])
                    except tk.TclError:
                        pass
            
            elif isinstance(widget, tk.Label):
                widget.configure(bg=theme["frame_bg"], fg=theme["fg"])
            
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=theme["button_bg"], 
                    fg=theme["button_fg"],
                    activebackground=theme["button_active_bg"],
                    activeforeground=theme["button_fg"],
                    relief="flat",
                    bd=1
                )
            
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    bg=theme["entry_bg"], 
                    fg=theme["entry_fg"],
                    insertbackground=theme["fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"]
                )
            
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=theme["text_bg"], 
                    fg=theme["text_fg"],
                    insertbackground=theme["fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"]
                )
            
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    bg=theme["entry_bg"], 
                    fg=theme["entry_fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"]
                )
            
            elif isinstance(widget, (tk.Scale, tk.Scrollbar)):
                widget.configure(
                    bg=theme["frame_bg"], 
                    fg=theme["fg"],
                    troughcolor=theme["entry_bg"],
                    activebackground=theme["accent"]
                )
            
            elif isinstance(widget, (tk.Checkbutton, tk.Radiobutton)):
                widget.configure(
                    bg=theme["frame_bg"],
                    fg=theme["fg"],
                    selectcolor=theme["entry_bg"],
                    activebackground=theme["hover"],
                    activeforeground=theme["fg"]
                )
            
            elif isinstance(widget, tk.Menu):
                widget.configure(
                    bg=theme["menu_bg"],
                    fg=theme["menu_fg"],
                    activebackground=theme["select_bg"],
                    activeforeground=theme["select_fg"]
                )
                
        except tk.TclError as e:
            # Some widgets might not support certain configuration options
            pass
    
    def apply_theme_recursive(self, parent):
        """Apply theme to parent and all its children recursively"""
        self.apply_theme_to_widget(parent)
        
        try:
            for child in parent.winfo_children():
                self.apply_theme_to_widget(child)
                if hasattr(child, 'winfo_children'):
                    self.apply_theme_recursive(child)
        except tk.TclError:
            pass
    
    def configure_ttk_style(self):
        """Configure ttk widget styles for current theme"""
        theme = self.get_theme()
        style = ttk.Style()
        
        # Use clam theme as base
        style.theme_use('clam')
        
        # Configure notebook
        style.configure('TNotebook', 
                       background=theme["frame_bg"],
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=theme["tab_bg"],
                       foreground=theme["tab_fg"],
                       padding=[12, 8],
                       borderwidth=1)
        style.map('TNotebook.Tab',
                 background=[('selected', theme["tab_active_bg"]),
                           ('active', theme["hover"])],
                 foreground=[('selected', theme["tab_active_fg"])])
        
        # Configure frame
        style.configure('TFrame', background=theme["frame_bg"])
        
        # Configure label
        style.configure('TLabel', 
                       background=theme["frame_bg"], 
                       foreground=theme["fg"])
        
        # Configure button
        style.configure('TButton', 
                       background=theme["button_bg"],
                       foreground=theme["button_fg"],
                       borderwidth=1,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', theme["button_active_bg"]),
                           ('pressed', theme["select_bg"])],
                 foreground=[('active', theme["button_fg"])])
        
        # Configure combobox
        style.configure('TCombobox',
                       fieldbackground=theme["entry_bg"],
                       background=theme["button_bg"],
                       foreground=theme["entry_fg"])
        
        # Configure progressbar
        style.configure('TProgressbar',
                       background=theme["accent"],
                       troughcolor=theme["entry_bg"])
    
    def get_matplotlib_style(self):
        """Get matplotlib style parameters for current theme"""
        theme = self.get_theme()
        
        if self.current_theme == "dark":
            return {
                'figure.facecolor': theme["bg"],
                'axes.facecolor': theme["frame_bg"],
                'axes.edgecolor': theme["border"],
                'axes.labelcolor': theme["fg"],
                'text.color': theme["fg"],
                'xtick.color': theme["fg"],
                'ytick.color': theme["fg"],
                'grid.color': theme["border"],
                'axes.prop_cycle': "cycler('color', ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0', '#00BCD4'])"
            }
        else:
            return {
                'figure.facecolor': theme["bg"],
                'axes.facecolor': theme["bg"],
                'axes.edgecolor': theme["border"],
                'axes.labelcolor': theme["fg"],
                'text.color': theme["fg"],
                'xtick.color': theme["fg"],
                'ytick.color': theme["fg"],
                'grid.color': theme["border"],
                'axes.prop_cycle': "cycler('color', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])"
            }

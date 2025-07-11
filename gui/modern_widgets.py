"""
Modern UI Widgets
Custom modern-styled widgets for enhanced user experience
"""

import tkinter as tk
from tkinter import ttk

class ModernButton(tk.Button):
    """Modern styled button with hover effects"""
    
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # Define color schemes
        self.color_schemes = {
            "primary": {
                "bg": "#2563eb",
                "fg": "white",
                "hover_bg": "#1d4ed8",
                "active_bg": "#1e40af"
            },
            "success": {
                "bg": "#10b981",
                "fg": "white", 
                "hover_bg": "#059669",
                "active_bg": "#047857"
            },
            "danger": {
                "bg": "#ef4444",
                "fg": "white",
                "hover_bg": "#dc2626",
                "active_bg": "#b91c1c"
            },
            "warning": {
                "bg": "#f59e0b",
                "fg": "white",
                "hover_bg": "#d97706",
                "active_bg": "#b45309"
            },
            "info": {
                "bg": "#06b6d4",
                "fg": "white",
                "hover_bg": "#0891b2",
                "active_bg": "#0e7490"
            },
            "secondary": {
                "bg": "#6b7280",
                "fg": "white",
                "hover_bg": "#4b5563",
                "active_bg": "#374151"
            }
        }
        
        self.style = style
        colors = self.color_schemes.get(style, self.color_schemes["primary"])
        
        # Default button configuration
        default_config = {
            "text": text,
            "command": command,
            "bg": colors["bg"],
            "fg": colors["fg"],
            "font": ("Segoe UI", 11, "bold"),
            "relief": "flat",
            "borderwidth": 0,
            "padx": 20,
            "pady": 10,
            "cursor": "hand2",
            "activebackground": colors["active_bg"],
            "activeforeground": colors["fg"]
        }
        
        # Merge with user provided kwargs
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        # Store colors for hover effects
        self.normal_bg = colors["bg"]
        self.hover_bg = colors["hover_bg"]
        self.active_bg = colors["active_bg"]
        
        # Bind hover events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_hover(self, event):
        """Handle mouse hover"""
        self.config(bg=self.hover_bg)
    
    def on_leave(self, event):
        """Handle mouse leave"""
        self.config(bg=self.normal_bg)
    
    def on_click(self, event):
        """Handle mouse click"""
        self.config(bg=self.active_bg)
    
    def on_release(self, event):
        """Handle mouse release"""
        self.config(bg=self.hover_bg)

class ModernFrame(tk.Frame):
    """Modern styled frame with rounded corners effect"""
    
    def __init__(self, parent, style="card", **kwargs):
        # Define frame styles
        self.styles = {
            "card": {
                "bg": "#ffffff",
                "relief": "solid",
                "bd": 1,
                "padx": 0,
                "pady": 0
            },
            "surface": {
                "bg": "#f1f5f9",
                "relief": "flat",
                "bd": 0,
                "padx": 10,
                "pady": 10
            },
            "dark": {
                "bg": "#1e293b",
                "relief": "flat",
                "bd": 0,
                "padx": 10,
                "pady": 10
            }
        }
        
        # Get style configuration
        style_config = self.styles.get(style, self.styles["card"])
        style_config.update(kwargs)
        
        super().__init__(parent, **style_config)

class ModernScale(tk.Scale):
    """Modern styled scale/slider"""
    
    def __init__(self, parent, **kwargs):
        # Modern scale configuration
        default_config = {
            "orient": "horizontal",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
            "troughcolor": "#e2e8f0",
            "bg": "#ffffff",
            "fg": "#1e293b",
            "activebackground": "#2563eb",
            "font": ("Segoe UI", 10)
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)

class ModernEntry(tk.Entry):
    """Modern styled entry widget"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = "#9ca3af"
        self.normal_color = "#1f2937"
        
        # Modern entry configuration
        default_config = {
            "font": ("Segoe UI", 11),
            "relief": "solid",
            "bd": 2,
            "highlightthickness": 0,
            "insertwidth": 2,
            "fg": self.normal_color,
            "bg": "#ffffff",
            "selectbackground": "#dbeafe",
            "selectforeground": "#1e40af"
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)
        
        # Add placeholder functionality
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            
            self.bind("<FocusIn>", self.on_focus_in)
            self.bind("<FocusOut>", self.on_focus_out)
    
    def on_focus_in(self, event):
        """Handle focus in"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.normal_color)
    
    def on_focus_out(self, event):
        """Handle focus out"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
    
    def get_value(self):
        """Get actual value (excluding placeholder)"""
        value = self.get()
        return "" if value == self.placeholder else value

class ModernLabel(tk.Label):
    """Modern styled label"""
    
    def __init__(self, parent, text="", style="normal", **kwargs):
        # Define label styles
        self.styles = {
            "title": {
                "font": ("Segoe UI", 24, "bold"),
                "fg": "#1e293b"
            },
            "heading": {
                "font": ("Segoe UI", 18, "bold"),
                "fg": "#1e293b"
            },
            "subheading": {
                "font": ("Segoe UI", 14, "bold"),
                "fg": "#374151"
            },
            "normal": {
                "font": ("Segoe UI", 11),
                "fg": "#4b5563"
            },
            "small": {
                "font": ("Segoe UI", 9),
                "fg": "#6b7280"
            },
            "accent": {
                "font": ("Segoe UI", 11, "bold"),
                "fg": "#2563eb"
            },
            "success": {
                "font": ("Segoe UI", 11, "bold"),
                "fg": "#059669"
            },
            "danger": {
                "font": ("Segoe UI", 11, "bold"),
                "fg": "#dc2626"
            },
            "warning": {
                "font": ("Segoe UI", 11, "bold"),
                "fg": "#d97706"
            }
        }
        
        # Default configuration
        default_config = {
            "text": text,
            "bg": "#ffffff",
            "anchor": "w"
        }
        
        # Apply style
        style_config = self.styles.get(style, self.styles["normal"])
        default_config.update(style_config)
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)

class ModernCheckbutton(tk.Checkbutton):
    """Modern styled checkbutton"""
    
    def __init__(self, parent, text="", **kwargs):
        # Modern checkbutton configuration
        default_config = {
            "text": text,
            "font": ("Segoe UI", 11),
            "fg": "#1f2937",
            "bg": "#ffffff",
            "activebackground": "#f3f4f6",
            "activeforeground": "#1f2937",
            "selectcolor": "#ffffff",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
            "cursor": "hand2"
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)

class ModernProgressbar(ttk.Progressbar):
    """Modern styled progressbar"""
    
    def __init__(self, parent, **kwargs):
        # Configure style
        style = ttk.Style()
        style.configure("Modern.Horizontal.TProgressbar",
                       background="#2563eb",
                       troughcolor="#e5e7eb",
                       borderwidth=0,
                       lightcolor="#2563eb",
                       darkcolor="#2563eb")
        
        default_config = {
            "style": "Modern.Horizontal.TProgressbar",
            "length": 300,
            "mode": "determinate"
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)

class ModernCard(tk.Frame):
    """Modern card container with header and content"""
    
    def __init__(self, parent, title="", **kwargs):
        # Card configuration
        default_config = {
            "bg": "#ffffff",
            "relief": "solid",
            "bd": 1
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)
        
        if title:
            # Create header
            self.header_frame = tk.Frame(self, bg="#2563eb")
            self.header_frame.pack(fill="x")
            
            self.title_label = ModernLabel(self.header_frame, text=title,
                                          style="subheading", fg="white", bg="#2563eb")
            self.title_label.pack(anchor="w", padx=15, pady=10)
        
        # Create content frame
        self.content_frame = tk.Frame(self, bg="#ffffff")
        self.content_frame.pack(fill="both", expand=True)
    
    def get_content_frame(self):
        """Get the content frame for adding widgets"""
        return self.content_frame

class ModernNotebook(ttk.Notebook):
    """Modern styled notebook/tabs"""
    
    def __init__(self, parent, **kwargs):
        # Configure modern tab style
        style = ttk.Style()
        
        # Configure tab appearance
        style.configure("Modern.TNotebook.Tab",
                       padding=[20, 10],
                       font=("Segoe UI", 11, "bold"))
        
        style.map("Modern.TNotebook.Tab",
                 background=[("selected", "#2563eb"),
                           ("active", "#3b82f6"),
                           ("!active", "#f1f5f9")],
                 foreground=[("selected", "white"),
                           ("active", "white"),
                           ("!active", "#4b5563")])
        
        default_config = {
            "style": "Modern.TNotebook"
        }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)
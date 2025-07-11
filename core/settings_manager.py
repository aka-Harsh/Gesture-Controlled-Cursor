"""
Settings Manager Module
Handles application settings and persistence
"""

import json
import os

class SettingsManager:
    def __init__(self, settings_file="gesture_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "use_gpu": False,
            "bookmarks": ["", "", "", ""],
            "cursor_sensitivity": 0.7,
            "click_rate": 2.0,
            "gesture_threshold": 0.8,
            "stability_zone": 15,
            "camera_resolution": [640, 480],
            "show_visual_feedback": True,
            "window_theme": "modern",
            "auto_start_camera": True,
            "emergency_hotkey": "ctrl+alt+q"
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    
                    # Merge with defaults for missing keys
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    
                    # Validate settings
                    settings = self.validate_settings(settings)
                    
                    print("✅ Settings loaded successfully")
                    return settings
        except Exception as e:
            print(f"⚠️ Error loading settings: {e}")
        
        print("📝 Using default settings")
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            # Create backup
            if os.path.exists(self.settings_file):
                backup_file = self.settings_file + ".backup"
                os.rename(self.settings_file, backup_file)
            
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            
            print("✅ Settings saved successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            
            # Restore backup if save failed
            backup_file = self.settings_file + ".backup"
            if os.path.exists(backup_file):
                os.rename(backup_file, self.settings_file)
            
            return False
    
    def validate_settings(self, settings):
        """Validate and correct settings values"""
        # Clamp numeric values to reasonable ranges
        settings["cursor_sensitivity"] = max(0.1, min(1.0, settings["cursor_sensitivity"]))
        settings["click_rate"] = max(0.5, min(10.0, settings["click_rate"]))
        settings["gesture_threshold"] = max(0.3, min(1.0, settings["gesture_threshold"]))
        settings["stability_zone"] = max(1, min(100, settings["stability_zone"]))
        
        # Validate camera resolution
        if not isinstance(settings["camera_resolution"], list) or len(settings["camera_resolution"]) != 2:
            settings["camera_resolution"] = [640, 480]
        else:
            settings["camera_resolution"][0] = max(320, min(1920, settings["camera_resolution"][0]))
            settings["camera_resolution"][1] = max(240, min(1080, settings["camera_resolution"][1]))
        
        # Validate bookmarks
        if not isinstance(settings["bookmarks"], list) or len(settings["bookmarks"]) != 4:
            settings["bookmarks"] = ["", "", "", ""]
        
        # Ensure all bookmark entries are strings
        for i in range(4):
            if not isinstance(settings["bookmarks"][i], str):
                settings["bookmarks"][i] = ""
        
        return settings
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def update(self, new_settings):
        """Update multiple settings"""
        self.settings.update(new_settings)
        self.settings = self.validate_settings(self.settings)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def export_settings(self, filepath):
        """Export settings to a file"""
        try:
            with open(filepath, "w") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, filepath):
        """Import settings from a file"""
        try:
            with open(filepath, "r") as f:
                imported_settings = json.load(f)
            
            # Merge with current settings
            self.settings.update(imported_settings)
            self.settings = self.validate_settings(self.settings)
            
            return self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
"""
Configuration management for Background Video Generator.
Handles loading, saving, and managing application settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration management class."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration with default values."""
        self.config_file = config_file
        self.default_config = {
            "api_key": "",
            "search_term": "nature",
            "duration": 300,  # seconds
            "resolution": "1920x1080",
            "aspect_ratio": "horizontal",
            "window_geometry": "800x600+100+100",
            "last_output_dir": "",
            "max_clips": 10,
            "min_clip_duration": 5,
            "max_clip_duration": 30
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self.config[key] = value
        self.save_config()
    
    def get_api_key(self) -> str:
        """Get Pexels API key."""
        return self.get("api_key", "")
    
    def set_api_key(self, api_key: str) -> None:
        """Set Pexels API key."""
        self.set("api_key", api_key)
    
    def get_search_term(self) -> str:
        """Get search term."""
        return self.get("search_term", "nature")
    
    def set_search_term(self, search_term: str) -> None:
        """Set search term."""
        self.set("search_term", search_term)
    
    def get_duration(self) -> int:
        """Get target duration in seconds."""
        return self.get("duration", 300)
    
    def set_duration(self, duration: int) -> None:
        """Set target duration in seconds."""
        self.set("duration", duration)
    
    def get_resolution(self) -> str:
        """Get target resolution."""
        return self.get("resolution", "1920x1080")
    
    def set_resolution(self, resolution: str) -> None:
        """Set target resolution."""
        self.set("resolution", resolution)
    
    def get_aspect_ratio(self) -> str:
        """Get aspect ratio preference."""
        return self.get("aspect_ratio", "horizontal")
    
    def set_aspect_ratio(self, aspect_ratio: str) -> None:
        """Set aspect ratio preference."""
        self.set("aspect_ratio", aspect_ratio)
    
    def get_window_geometry(self) -> str:
        """Get window geometry."""
        return self.get("window_geometry", "800x600+100+100")
    
    def set_window_geometry(self, geometry: str) -> None:
        """Set window geometry."""
        self.set("window_geometry", geometry)
    
    def get_output_dir(self) -> str:
        """Get last output directory."""
        return self.get("last_output_dir", "")
    
    def set_output_dir(self, output_dir: str) -> None:
        """Set last output directory."""
        self.set("last_output_dir", output_dir)
    
    def get_max_clips(self) -> int:
        """Get maximum number of clips to download."""
        return self.get("max_clips", 10)
    
    def set_max_clips(self, max_clips: int) -> None:
        """Set maximum number of clips to download."""
        self.set("max_clips", max_clips)
    
    def get_min_clip_duration(self) -> int:
        """Get minimum clip duration in seconds."""
        return self.get("min_clip_duration", 5)
    
    def set_min_clip_duration(self, duration: int) -> None:
        """Set minimum clip duration in seconds."""
        self.set("min_clip_duration", duration)
    
    def get_max_clip_duration(self) -> int:
        """Get maximum clip duration in seconds."""
        return self.get("max_clip_duration", 30)
    
    def set_max_clip_duration(self, duration: int) -> None:
        """Set maximum clip duration in seconds."""
        self.set("max_clip_duration", duration) 
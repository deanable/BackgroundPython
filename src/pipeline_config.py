"""
Configuration management for the video processing pipeline.
"""

import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ProcessingConfig:
    """Configuration for video processing pipeline."""
    
    # General settings
    max_workers: int = 2
    temp_dir: str = "temp"
    output_dir: str = "output"
    log_level: str = "INFO"
    
    # Quality settings
    min_quality_score: float = 0.7
    max_compression_ratio: float = 0.5
    target_bitrate_factor: float = 0.8
    
    # Duration settings
    min_clip_duration: int = 1
    max_clip_duration: int = 300
    default_fade_duration: float = 0.5
    
    # Preset configurations
    presets: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize presets if not provided."""
        if self.presets is None:
            self.presets = {
                "social_media": {
                    "resolution": (1080, 1920),  # 9:16 vertical
                    "fps": 30,
                    "bitrate": 8000,
                    "codec": "h264",
                    "audio_bitrate": 128,
                    "format": "mp4"
                },
                "presentation": {
                    "resolution": (1920, 1080),  # 16:9 horizontal
                    "fps": 30,
                    "bitrate": 10000,
                    "codec": "h264",
                    "audio_bitrate": 192,
                    "format": "mp4"
                },
                "mobile": {
                    "resolution": (720, 1280),  # 9:16 vertical
                    "fps": 30,
                    "bitrate": 4000,
                    "codec": "h264",
                    "audio_bitrate": 96,
                    "format": "mp4"
                },
                "high_quality": {
                    "resolution": (1920, 1080),
                    "fps": 60,
                    "bitrate": 20000,
                    "codec": "h264",
                    "audio_bitrate": 320,
                    "format": "mp4"
                }
            }

class ConfigManager:
    """Manages configuration loading and saving."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize config manager."""
        self.config_path = config_path
        self.config = ProcessingConfig()
        
    def load_config(self) -> ProcessingConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.config = ProcessingConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return self.config
    
    def save_config(self, config: ProcessingConfig = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = self.config
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_preset(self, preset_name: str, preset_config: Dict[str, Any]) -> None:
        """Update or add a preset configuration."""
        self.config.presets[preset_name] = preset_config
        self.save_config()
    
    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """Get preset configuration."""
        return self.config.presets.get(preset_name, {})
    
    def list_presets(self) -> List[str]:
        """List available presets."""
        return list(self.config.presets.keys())

# Global config instance
config_manager = ConfigManager()
processing_config = config_manager.load_config()

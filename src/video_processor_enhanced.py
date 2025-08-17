"""
Enhanced video processing module with intelligent duration control.
Extends the base VideoProcessor with advanced features.
"""

import os
import random
from typing import List, Dict, Any, Optional
from src.video_processor import VideoProcessor

class EnhancedVideoProcessor(VideoProcessor):
    """Enhanced video processor with intelligent duration control."""
    
    def __init__(self, logger):
        """Initialize enhanced video processor."""
        super().__init__(logger)
        self.processing_cache = {}
        
    def intelligent_duration_extension(self, video_paths: List[str], target_duration: int, 
                                     min_clip_duration: int = 3) -> List[str]:
        """
        Intelligently extend clips to reach target duration using partial clips
        and smart selection based on content analysis.
        """
        if not video_paths:
            return []
        
        # Calculate total available duration
        total_available = self.calculate_total_duration(video_paths)
        
        if total_available >= target_duration:
            return video_paths
        
        # Calculate how much additional content we need
        additional_needed = target_duration - total_available
        
        # Create weighted selection based on clip durations
        clip_weights = []
        for path in video_paths:
            duration = self.get_video_duration(path)
            if duration >= min_clip_duration:
                # Prefer longer clips for extension
                weight = min(duration, 10)  # Cap weight at 10 seconds
                clip_weights.append((path, duration, weight))
        
        if not clip_weights:
            return video_paths
        
        # Sort by weight (descending) to use best clips first
        clip_weights.sort(key=lambda x: x[2], reverse=True)
        
        extended_paths = video_paths.copy()
        
        # Add clips until we reach target duration
        current_total = total_available
        
        while current_total < target_duration and clip_weights:
            # Select next best clip
            best_clip_path, clip_duration, _ = clip_weights[0]
            
            # Calculate how much of this clip to use
            remaining_needed = target_duration - current_total
            use_duration = min(clip_duration, remaining_needed)
            
            # Add the clip (can be partial)
            extended_paths.append(best_clip_path)
            current_total += use_duration
            
            # If we've used this clip completely, remove it
            if use_duration >= clip_duration:
                clip_weights.pop(0)
        
        return extended_paths
    
    def create_processing_preset(self, preset_name: str) -> Dict[str, Any]:
        """Create processing presets for different use cases."""
        presets = {
            "social_media": {
                "target_resolution": "1080x1920",
                "target_fps": 30,
                "aspect_ratio": "vertical",
                "quality": "high"
            },
            "presentation": {
                "target_resolution": "1920x1080",
                "target_fps": 30,
                "aspect_ratio": "horizontal",
                "quality": "medium"
            },
            "mobile": {
                "target_resolution": "720x1280",
                "target_fps": 24,
                "aspect_ratio": "vertical",
                "quality": "medium"
            },
            "high_quality": {
                "target_resolution": "1920x1080",
                "target_fps": 60,
                "aspect_ratio": "horizontal",
                "quality": "high"
            }
        }
        
        return presets.get(preset_name, presets["presentation"])
    
    def validate_output_quality(self, output_path: str, min_bitrate: int = 1000) -> bool:
        """Validate the quality of the processed video."""
        try:
            info = self.get_video_info(output_path)
            if not info or 'format' not in info:
                return False
            
            # Check bitrate
            bitrate = int(info['format'].get('bit_rate', 0)) / 1000  # Convert to kbps
            if bitrate < min_bitrate:
                self.logger.warning(f"Output video bitrate ({bitrate:.0f}kbps) is below minimum ({min_bitrate}kbps)")
                return False
            
            # Check resolution
            video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
            if not video_stream:
                return False
            
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            if width < 640 or height < 360:
                self.logger.warning(f"Output video resolution ({width}x{height}) is too low")
                return False
            
            return True
            
        except Exception as e:
            self.logger.exception(e, "Validating output quality")
            return False
    
    def process_with_preset(self, video_paths: List[str], preset_name: str, target_duration: int, 
                           output_path: str, progress_callback=None) -> bool:
        """Process videos using a predefined preset."""
        preset = self.create_processing_preset(preset_name)
        
        return self.process_videos_with_progress(
            video_paths=video_paths,
            target_duration=target_duration,
            target_resolution=preset["target_resolution"],
            output_path=output_path,
            progress_callback=progress_callback,
            aspect_ratio=preset["aspect_ratio"]
        )

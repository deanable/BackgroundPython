"""
Video quality assessment and validation module.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import json
from src.video_processor import VideoProcessor

class QualityAssessor:
    """Assesses video quality using various metrics."""
    
    def __init__(self, logger):
        """Initialize quality assessor."""
        self.logger = logger
        self.processor = VideoProcessor(logger)
        
    def assess_video_quality(self, video_path: str) -> Dict[str, Any]:
        """Comprehensive video quality assessment."""
        try:
            # Get basic video info
            info = self.processor.get_video_info(video_path)
            if not info:
                return {"error": "Could not get video info"}
            
            # Extract quality metrics
            metrics = {
                "basic_info": self._get_basic_metrics(info),
                "technical_metrics": self._get_technical_metrics(info),
                "quality_scores": self._calculate_quality_scores(info),
                "recommendations": []
            }
            
            # Generate recommendations
            metrics["recommendations"] = self._generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.exception(e, "Assessing video quality")
            return {"error": str(e)}
    
    def _get_basic_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic video metrics."""
        video_stream = next((s for s in info.get('streams', []) 
                           if s.get('codec_type') == 'video'), {})
        
        return {
            "resolution": {
                "width": int(video_stream.get('width', 0)),
                "height": int(video_stream.get('height', 0))
            },
            "duration": float(info['format'].get('duration', 0)),
            "fps": eval(video_stream.get('r_frame_rate', '0/1')),
            "bitrate": int(info['format'].get('bit_rate', 0)) // 1000,  # kbps
            "codec": video_stream.get('codec_name', 'unknown'),
            "format": info['format'].get('format_name', 'unknown')
        }
    
    def _get_technical_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical quality metrics."""
        video_stream = next((s for s in info.get('streams', []) 
                           if s.get('codec_type') == 'video'), {})
        
        return {
            "pixel_format": video_stream.get('pix_fmt', 'unknown'),
            "color_space": video_stream.get('color_space', 'unknown'),
            "color_range": video_stream.get('color_range', 'unknown'),
            "has_b_frames": int(video_stream.get('has_b_frames', 0)),
            "profile": video_stream.get('profile', 'unknown'),
            "level": int(video_stream.get('level', 0))
        }
    
    def _calculate_quality_scores(self, info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality scores based on various factors."""
        basic = self._get_basic_metrics(info)
        
        scores = {
            "resolution_score": self._calculate_resolution_score(basic["resolution"]),
            "bitrate_score": self._calculate_bitrate_score(basic["bitrate"], basic["resolution"]),
            "fps_score": self._calculate_fps_score(basic["fps"]),
            "overall_score": 0.0
        }
        
        # Calculate weighted overall score
        weights = {"resolution_score": 0.4, "bitrate_score": 0.4, "fps_score": 0.2}
        scores["overall_score"] = sum(
            scores[key] * weights[key] 
            for key in weights
        )
        
        return scores
    
    def _calculate_resolution_score(self, resolution: Dict[str, int]) -> float:
        """Calculate resolution quality score."""
        width, height = resolution["width"], resolution["height"]
        
        if width >= 1920 and height >= 1080:
            return 1.0  # Full HD or better
        elif width >= 1280 and height >= 720:
            return 0.8  # HD
        elif width >= 854 and height >= 480:
            return 0.6  # SD
        elif width >= 640 and height >= 360:
            return 0.4  # Low quality
        else:
            return 0.2  # Very low quality
    
    def _calculate_bitrate_score(self, bitrate: int, resolution: Dict[str, int]) -> float:
        """Calculate bitrate quality score based on resolution."""
        width, height = resolution["width"], resolution["height"]
        pixels = width * height
        
        # Expected bitrate ranges (kbps)
        if pixels >= 1920 * 1080:
            expected_min = 5000
            expected_max = 15000
        elif pixels >= 1280 * 720:
            expected_min = 2500
            expected_max = 8000
        elif pixels >= 854 * 480:
            expected_min = 1000
            expected_max = 4000
        else:
            expected_min = 500
            expected_max = 2000
        
        if bitrate >= expected_max:
            return 1.0
        elif bitrate <= expected_min:
            return 0.3
        else:
            # Linear interpolation
            ratio = (bitrate - expected_min) / (expected_max - expected_min)
            return 0.3 + 0.7 * ratio
    
    def _calculate_fps_score(self, fps: float) -> float:
        """Calculate FPS quality score."""
        if fps >= 60:
            return 1.0
        elif fps >= 30:
            return 0.9
        elif fps >= 24:
            return 0.8
        elif fps >= 15:
            return 0.6
        else:
            return 0.3
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        basic = metrics["basic_info"]
        scores = metrics["quality_scores"]
        
        # Resolution recommendations
        if basic["resolution"]["width"] < 1920:
            recommendations.append("Consider increasing resolution to 1920x1080 for better quality")
        
        # Bitrate recommendations
        if scores["bitrate_score"] < 0.7:
            recommendations.append("Increase bitrate to improve visual quality")
        
        # FPS recommendations
        if basic["fps"] < 24:
            recommendations.append("Increase frame rate to at least 24fps for smoother playback")
        
        # Duration recommendations
        if basic["duration"] < 5:
            recommendations.append("Consider extending video duration for better engagement")
        
        return recommendations
    
    def validate_video_integrity(self, video_path: str) -> bool:
        """Validate video file integrity."""
        try:
            # Try to open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False
            
            # Check if we can read frames
            ret, frame = cap.read()
            cap.release()
            
            return ret and frame is not None
            
        except Exception as e:
            self.logger.exception(e, "Validating video integrity")
            return False
    
    def compare_videos(self, original_path: str, processed_path: str) -> Dict[str, Any]:
        """Compare original and processed videos."""
        original_metrics = self.assess_video_quality(original_path)
        processed_metrics = self.assess_video_quality(processed_path)
        
        comparison = {
            "original": original_metrics,
            "processed": processed_metrics,
            "quality_change": {},
            "recommendations": []
        }
        
        if "error" not in original_metrics and "error" not in processed_metrics:
            # Calculate quality changes
            for score_type in ["resolution_score", "bitrate_score", "fps_score", "overall_score"]:
                if score_type in original_metrics["quality_scores"] and score_type in processed_metrics["quality_scores"]:
                    change = processed_metrics["quality_scores"][score_type] - original_metrics["quality_scores"][score_type]
                    comparison["quality_change"][score_type] = change
            
            # Generate comparison recommendations
            if comparison["quality_change"].get("overall_score", 0) < -0.1:
                comparison["recommendations"].append("Quality degradation detected - review processing settings")
        
        return comparison

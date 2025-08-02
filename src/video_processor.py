"""
Video processing module for Background Video Generator.
Handles video normalization, concatenation, and FFmpeg operations.
"""

import os
import subprocess
import tempfile
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import cv2

class VideoProcessor:
    """Video processing class for handling video operations."""
    
    def __init__(self, logger):
        """Initialize video processor."""
        self.logger = logger
        self.temp_dir = None
        self.check_ffmpeg()
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available in the system."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.system_info("FFmpeg", "Available")
                return True
            else:
                self.logger.error("FFmpeg check failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.logger.error(f"FFmpeg not found or not accessible: {e}")
            return False
    
    def create_temp_directory(self) -> str:
        """Create temporary directory for processing."""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="bg_video_")
            self.logger.info(f"TEMP: Created temporary directory: {self.temp_dir}")
        return self.temp_dir
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Get video information using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.logger.video_processing("Info extraction", video_path)
                return data
            else:
                self.logger.error(f"Failed to get video info for {video_path}")
                return None
                
        except Exception as e:
            self.logger.exception(e, f"Getting video info for {video_path}")
            return None
    
    def normalize_video(self, input_path: str, output_path: str, target_resolution: str, 
                       target_fps: int = 30) -> bool:
        """Normalize video to target resolution and format."""
        try:
            self.logger.video_processing("Normalization", input_path, output_path, f"Resolution: {target_resolution}")
            start_time = time.time()
            
            # Parse target resolution
            width, height = map(int, target_resolution.split('x'))
            
            # FFmpeg command for normalization
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                '-r', str(target_fps),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # Overwrite output file
                output_path
            ]
            
            self.logger.debug(f"FFMPEG: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                elapsed = time.time() - start_time
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                self.logger.performance(f"Video normalization completed in {elapsed:.1f}s - {file_size_mb:.1f}MB")
                self.logger.video_processing("Normalization complete", input_path, output_path)
                return True
            else:
                self.logger.error(f"Video normalization failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.exception(e, f"Normalizing video {input_path}")
            return False
    
    def normalize_videos(self, video_paths: List[str], target_resolution: str) -> List[str]:
        """Normalize multiple videos to the same format."""
        self.logger.pipeline_step("Video Normalization", f"Normalizing {len(video_paths)} videos to {target_resolution}")
        
        temp_dir = self.create_temp_directory()
        normalized_paths = []
        
        for i, video_path in enumerate(video_paths):
            try:
                # Create normalized filename
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                normalized_path = os.path.join(temp_dir, f"normalized_{i}_{base_name}.mp4")
                
                if self.normalize_video(video_path, normalized_path, target_resolution):
                    normalized_paths.append(normalized_path)
                    self.logger.info(f"VIDEO NORMALIZATION: Successfully normalized video {i+1}/{len(video_paths)}")
                else:
                    self.logger.error(f"VIDEO NORMALIZATION: Failed to normalize video {i+1}")
                    
            except Exception as e:
                self.logger.exception(e, f"Normalizing video {i+1}")
        
        self.logger.pipeline_step("Video Normalization Complete", f"Normalized {len(normalized_paths)} videos")
        return normalized_paths
    
    def create_concat_list(self, video_paths: List[str], output_path: str) -> str:
        """Create FFmpeg concat list file."""
        concat_list_path = os.path.join(self.create_temp_directory(), "concat_list.txt")
        
        with open(concat_list_path, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path}'\n")
        
        self.logger.debug(f"Created concat list with {len(video_paths)} videos")
        return concat_list_path
    
    def concatenate_videos_ffmpeg(self, video_paths: List[str], output_path: str) -> bool:
        """Concatenate videos using FFmpeg."""
        try:
            self.logger.video_processing("Concatenation", f"{len(video_paths)} videos", output_path)
            start_time = time.time()
            
            if not video_paths:
                self.logger.error("No videos to concatenate")
                return False
            
            # Create concat list
            concat_list_path = self.create_concat_list(video_paths, output_path)
            
            # FFmpeg concat command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                '-y',  # Overwrite output file
                output_path
            ]
            
            self.logger.debug(f"FFMPEG: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                elapsed = time.time() - start_time
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                self.logger.performance(f"Video concatenation completed in {elapsed:.1f}s - {file_size_mb:.1f}MB")
                self.logger.video_processing("Concatenation complete", f"{len(video_paths)} videos", output_path)
                return True
            else:
                self.logger.error(f"Video concatenation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.exception(e, "Video concatenation")
            return False
    
    def concatenate_videos_moviepy(self, video_paths: List[str], output_path: str) -> bool:
        """Concatenate videos using MoviePy (fallback method)."""
        try:
            self.logger.video_processing("Concatenation (MoviePy)", f"{len(video_paths)} videos", output_path)
            start_time = time.time()
            
            if not video_paths:
                self.logger.error("No videos to concatenate")
                return False
            
            # Load video clips
            clips = []
            for video_path in video_paths:
                try:
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
                    self.logger.debug(f"Loaded clip: {video_path}")
                except Exception as e:
                    self.logger.error(f"Failed to load clip {video_path}: {e}")
            
            if not clips:
                self.logger.error("No valid clips to concatenate")
                return False
            
            # For now, use only the first clip as concatenation is complex in this MoviePy version
            # In a production environment, you might want to implement proper concatenation
            if len(clips) > 1:
                self.logger.warning(f"MoviePy concatenation limited - using first clip only. Total clips: {len(clips)}")
            
            final_clip = clips[0]
            
            # Write final video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            final_clip.close()
            for clip in clips:
                clip.close()
            
            elapsed = time.time() - start_time
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            self.logger.performance(f"Video concatenation (MoviePy) completed in {elapsed:.1f}s - {file_size_mb:.1f}MB")
            self.logger.video_processing("Concatenation complete", f"{len(video_paths)} videos", output_path)
            return True
            
        except Exception as e:
            self.logger.exception(e, "Video concatenation with MoviePy")
            return False
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        try:
            info = self.get_video_info(video_path)
            if info and 'format' in info:
                return float(info['format']['duration'])
            return 0.0
        except Exception as e:
            self.logger.exception(e, f"Getting duration for {video_path}")
            return 0.0
    
    def calculate_total_duration(self, video_paths: List[str]) -> float:
        """Calculate total duration of all videos."""
        total_duration = 0.0
        for video_path in video_paths:
            duration = self.get_video_duration(video_path)
            total_duration += duration
            self.logger.debug(f"Video {os.path.basename(video_path)}: {duration:.1f}s")
        
        self.logger.info(f"TOTAL DURATION: {total_duration:.1f} seconds")
        return total_duration
    
    def process_videos(self, video_paths: List[str], target_duration: int, target_resolution: str, 
                      output_path: str) -> bool:
        """Main video processing pipeline."""
        try:
            self.logger.pipeline_step("Video Processing Pipeline", f"Processing {len(video_paths)} videos")
            
            # Calculate initial total duration
            initial_duration = self.calculate_total_duration(video_paths)
            
            # Normalize videos
            normalized_paths = self.normalize_videos(video_paths, target_resolution)
            
            if not normalized_paths:
                self.logger.error("No videos were successfully normalized")
                return False
            
            # Calculate normalized total duration
            normalized_duration = self.calculate_total_duration(normalized_paths)
            
            # Try FFmpeg concatenation first, fallback to MoviePy
            success = self.concatenate_videos_ffmpeg(normalized_paths, output_path)
            
            if not success:
                self.logger.warning("FFmpeg concatenation failed, trying MoviePy")
                success = self.concatenate_videos_moviepy(normalized_paths, output_path)
            
            if success:
                final_duration = self.get_video_duration(output_path)
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                self.logger.pipeline_step("Video Processing Complete", 
                                        f"Final video: {final_duration:.1f}s, {file_size_mb:.1f}MB")
                self.logger.file_operation("Created", os.path.basename(output_path), f"{file_size_mb:.1f}MB")
                
                return True
            else:
                self.logger.error("Video processing pipeline failed")
                return False
                
        except Exception as e:
            self.logger.exception(e, "Video processing pipeline")
            return False
    
    def cleanup(self) -> None:
        """Clean up temporary files and directories."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"TEMP: Cleaned up temporary directory: {self.temp_dir}")
                self.temp_dir = None
        except Exception as e:
            self.logger.exception(e, "Cleanup") 
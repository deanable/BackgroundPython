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
try:
    from moviepy.video.compositing.concatenate import concatenate_videoclips
except ImportError:
    try:
        from moviepy.editor import concatenate_videoclips
    except ImportError:
        try:
            from moviepy import concatenate_videoclips
        except ImportError:
            concatenate_videoclips = None


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
    
    def flip_resolution_for_vertical(self, target_resolution: str, aspect_ratio: str) -> str:
        """Flip resolution dimensions for vertical aspect ratio."""
        if aspect_ratio == "vertical":
            width, height = map(int, target_resolution.split('x'))
            # Flip the dimensions for vertical videos
            flipped_resolution = f"{height}x{width}"
            self.logger.info(f"RESOLUTION FLIP: {target_resolution} -> {flipped_resolution} for vertical aspect ratio")
            return flipped_resolution
        return target_resolution

    def normalize_video(self, input_path: str, output_path: str, target_resolution: str, 
                       target_fps: int = 30, aspect_ratio: str = "horizontal") -> bool:
        """Normalize video to target resolution and format."""
        try:
            # Flip resolution if vertical aspect ratio is selected
            final_resolution = self.flip_resolution_for_vertical(target_resolution, aspect_ratio)
            
            self.logger.video_processing("Normalization", input_path, output_path, f"Resolution: {final_resolution}")
            start_time = time.time()
            
            # Parse target resolution
            width, height = map(int, final_resolution.split('x'))
            
            # FFmpeg command for normalization
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                '-r', str(target_fps),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-an',  # Exclude audio tracks
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
    
    def normalize_videos(self, video_paths: List[str], target_resolution: str, aspect_ratio: str = "horizontal") -> List[str]:
        """Normalize multiple videos to the same format."""
        self.logger.pipeline_step("Video Normalization", f"Normalizing {len(video_paths)} videos to {target_resolution}")
        
        temp_dir = self.create_temp_directory()
        normalized_paths = []
        
        for i, video_path in enumerate(video_paths):
            try:
                # Create normalized filename with temp prefix
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                normalized_path = os.path.join(temp_dir, f"temp_background_video_normalized_{i}_{base_name}.mp4")
                
                if self.normalize_video(video_path, normalized_path, target_resolution, aspect_ratio=aspect_ratio):
                    normalized_paths.append(normalized_path)
                    self.logger.info(f"VIDEO NORMALIZATION: Successfully normalized video {i+1}/{len(video_paths)}")
                else:
                    self.logger.error(f"VIDEO NORMALIZATION: Failed to normalize video {i+1}")
                    
            except Exception as e:
                self.logger.exception(e, f"Normalizing video {i+1}")
        
        self.logger.pipeline_step("Video Normalization Complete", f"Normalized {len(normalized_paths)} videos")
        return normalized_paths
    
    def normalize_videos_with_progress(self, video_paths: List[str], target_resolution: str, 
                                     progress_callback=None, aspect_ratio: str = "horizontal") -> List[str]:
        """Normalize multiple videos to the same format with progress callback."""
        self.logger.pipeline_step("Video Normalization", f"Normalizing {len(video_paths)} videos to {target_resolution}")
        
        temp_dir = self.create_temp_directory()
        normalized_paths = []
        
        for i, video_path in enumerate(video_paths):
            try:
                # Call progress callback for normalization step
                if progress_callback:
                    progress_callback(i + 1, len(video_paths), "normalizing")
                
                # Create normalized filename with temp prefix
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                normalized_path = os.path.join(temp_dir, f"temp_background_video_normalized_{i}_{base_name}.mp4")
                
                if self.normalize_video(video_path, normalized_path, target_resolution, aspect_ratio=aspect_ratio):
                    normalized_paths.append(normalized_path)
                    self.logger.info(f"VIDEO NORMALIZATION: Successfully normalized video {i+1}/{len(video_paths)}")
                else:
                    self.logger.error(f"VIDEO NORMALIZATION: Failed to normalize video {i+1}")
                    
            except Exception as e:
                self.logger.exception(e, f"Normalizing video {i+1}")
        
        # Call progress callback for normalization completion
        if progress_callback:
            progress_callback(len(video_paths), len(video_paths), "normalizing")
        
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
                '-c:v', 'copy',
                '-an',  # Exclude audio tracks
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
    
    def concatenate_videos_ffmpeg_with_progress(self, video_paths: List[str], output_path: str, 
                                              progress_callback=None) -> bool:
        """Concatenate videos using FFmpeg with progress callback."""
        try:
            self.logger.video_processing("Concatenation", f"{len(video_paths)} videos", output_path)
            start_time = time.time()
            
            if not video_paths:
                self.logger.error("No videos to concatenate")
                return False
            
            # Call progress callback for concatenation start
            if progress_callback:
                progress_callback(1, len(video_paths), "concatenating")
            
            # Create concat list
            concat_list_path = self.create_concat_list(video_paths, output_path)
            
            # FFmpeg concat command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c:v', 'copy',
                '-an',  # Exclude audio tracks
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
                
                # Call progress callback for concatenation completion
                if progress_callback:
                    progress_callback(len(video_paths), len(video_paths), "concatenating")
                
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
            
            if concatenate_videoclips is None:
                self.logger.error("MoviePy concatenation not available")
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
            
            # Concatenate clips
            if len(clips) > 1:
                self.logger.info(f"MoviePy: Concatenating {len(clips)} clips")
                final_clip = concatenate_videoclips(clips, method="compose")
            else:
                final_clip = clips[0]
            
            # Write final video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
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
    
    def concatenate_videos_moviepy_with_progress(self, video_paths: List[str], output_path: str, 
                                               progress_callback=None) -> bool:
        """Concatenate videos using MoviePy (fallback method) with progress callback."""
        try:
            self.logger.video_processing("Concatenation (MoviePy)", f"{len(video_paths)} videos", output_path)
            start_time = time.time()
            
            if not video_paths:
                self.logger.error("No videos to concatenate")
                return False
            
            if concatenate_videoclips is None:
                self.logger.error("MoviePy concatenation not available")
                return False
            
            # Load video clips with progress
            clips = []
            for i, video_path in enumerate(video_paths):
                try:
                    # Call progress callback for loading clips
                    if progress_callback:
                        progress_callback(i + 1, len(video_paths), "concatenating")
                    
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
                    self.logger.debug(f"Loaded clip: {video_path}")
                except Exception as e:
                    self.logger.error(f"Failed to load clip {video_path}: {e}")
            
            if not clips:
                self.logger.error("No valid clips to concatenate")
                return False
            
            # Concatenate clips
            if len(clips) > 1:
                self.logger.info(f"MoviePy: Concatenating {len(clips)} clips")
                final_clip = concatenate_videoclips(clips, method="compose")
            else:
                final_clip = clips[0]
            
            # Write final video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
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
    
    def extend_clips_to_duration(self, video_paths: List[str], target_duration: int) -> List[str]:
        """Extend clips by repeating them to reach target duration."""
        try:
            if not video_paths:
                return []
            
            # Calculate total duration of available clips
            total_available_duration = self.calculate_total_duration(video_paths)
            
            if total_available_duration == 0:
                self.logger.error("No valid video durations found")
                return video_paths
            
            self.logger.info(f"DURATION EXTENSION: Target: {target_duration}s, Available: {total_available_duration:.1f}s")
            
            # If we already have enough duration, don't repeat
            if total_available_duration >= target_duration:
                self.logger.info(f"DURATION CHECK: Available clips ({total_available_duration:.1f}s) are sufficient for target ({target_duration}s) - no repetition needed")
                return video_paths
            
            # Only repeat if we have less content than the target duration
            self.logger.warning(f"INSUFFICIENT CONTENT: Only {total_available_duration:.1f}s available for {target_duration}s target - repeating clips")
            
            # Calculate minimal repetitions needed
            import math
            repetitions_needed = math.ceil(target_duration / total_available_duration)
            self.logger.info(f"DURATION EXTENSION: Repeating clips {repetitions_needed} times to reach minimum duration")
            
            # Create extended list by repeating clips
            extended_paths = []
            for _ in range(repetitions_needed):
                extended_paths.extend(video_paths)
            
            # Calculate new total duration
            extended_duration = self.calculate_total_duration(extended_paths)
            self.logger.info(f"DURATION EXTENSION: Extended duration: {extended_duration:.1f}s")
            
            return extended_paths
            
        except Exception as e:
            self.logger.exception(e, "Extending clips to duration")
            return video_paths
    
    def trim_video_to_duration(self, input_path: str, output_path: str, target_duration: int) -> bool:
        """Trim video to exact target duration using FFmpeg."""
        try:
            self.logger.video_processing("Duration Trimming", input_path, output_path, f"Target: {target_duration}s")
            start_time = time.time()
            
            # FFmpeg command to trim video to exact duration
            cmd = [
                'ffmpeg', '-i', input_path,
                '-t', str(target_duration),  # Trim to target duration
                '-c:v', 'copy',  # Copy video codec (no re-encoding)
                '-an',  # Exclude audio tracks
                '-y',  # Overwrite output file
                output_path
            ]
            
            self.logger.debug(f"FFMPEG TRIM: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                elapsed = time.time() - start_time
                final_duration = self.get_video_duration(output_path)
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                self.logger.performance(f"Video trimming completed in {elapsed:.1f}s - Final duration: {final_duration:.1f}s, {file_size_mb:.1f}MB")
                self.logger.video_processing("Trimming complete", input_path, output_path, f"Final: {final_duration:.1f}s")
                return True
            else:
                self.logger.error(f"Video trimming failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.exception(e, f"Trimming video {input_path}")
            return False

    def process_videos(self, video_paths: List[str], target_duration: int, target_resolution: str, 
                      output_path: str, aspect_ratio: str = "horizontal") -> bool:
        """Main video processing pipeline with duration control."""
        try:
            self.logger.pipeline_step("Video Processing Pipeline", f"Processing {len(video_paths)} videos for {target_duration}s target")
            
            # Calculate initial total duration
            initial_duration = self.calculate_total_duration(video_paths)
            
            # Extend clips if needed to reach target duration
            extended_paths = self.extend_clips_to_duration(video_paths, target_duration)
            
            # Normalize videos
            normalized_paths = self.normalize_videos(extended_paths, target_resolution, aspect_ratio)
            
            if not normalized_paths:
                self.logger.error("No videos were successfully normalized")
                return False
            
            # Calculate normalized total duration
            normalized_duration = self.calculate_total_duration(normalized_paths)
            
            # Create temporary output path for concatenation
            temp_dir = self.create_temp_directory()
            temp_concat_path = os.path.join(temp_dir, "temp_concatenated.mp4")
            
            # Try FFmpeg concatenation first, fallback to MoviePy
            success = self.concatenate_videos_ffmpeg(normalized_paths, temp_concat_path)
            
            if not success:
                self.logger.warning("FFmpeg concatenation failed, trying MoviePy")
                success = self.concatenate_videos_moviepy(normalized_paths, temp_concat_path)
            
            if not success:
                self.logger.error("Video concatenation failed")
                return False
            
            # Check if we need to trim to exact duration
            concat_duration = self.get_video_duration(temp_concat_path)
            
            if concat_duration > target_duration:
                self.logger.info(f"DURATION CONTROL: Trimming video from {concat_duration:.1f}s to {target_duration}s")
                success = self.trim_video_to_duration(temp_concat_path, output_path, target_duration)
            else:
                # Duration is already correct or shorter, just copy the file
                import shutil
                shutil.copy2(temp_concat_path, output_path)
                success = True
            
            if success:
                final_duration = self.get_video_duration(output_path)
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                self.logger.pipeline_step("Video Processing Complete", 
                                        f"Final video: {final_duration:.1f}s (target: {target_duration}s), {file_size_mb:.1f}MB")
                self.logger.file_operation("Created", os.path.basename(output_path), f"{file_size_mb:.1f}MB")
                
                return True
            else:
                self.logger.error("Video processing pipeline failed")
                return False
                
        except Exception as e:
            self.logger.exception(e, "Video processing pipeline")
            return False
    
    def process_videos_with_progress(self, video_paths: List[str], target_duration: int, target_resolution: str, 
                                   output_path: str, progress_callback=None, aspect_ratio: str = "horizontal") -> bool:
        """Main video processing pipeline with progress callback and duration control."""
        try:
            self.logger.pipeline_step("Video Processing Pipeline", f"Processing {len(video_paths)} videos for {target_duration}s target")
            
            # Calculate initial total duration
            initial_duration = self.calculate_total_duration(video_paths)
            
            # Extend clips if needed to reach target duration
            extended_paths = self.extend_clips_to_duration(video_paths, target_duration)
            
            # Normalize videos with progress
            normalized_paths = self.normalize_videos_with_progress(extended_paths, target_resolution, progress_callback, aspect_ratio)
            
            if not normalized_paths:
                self.logger.error("No videos were successfully normalized")
                return False
            
            # Calculate normalized total duration
            normalized_duration = self.calculate_total_duration(normalized_paths)
            
            # Create temporary output path for concatenation
            temp_dir = self.create_temp_directory()
            temp_concat_path = os.path.join(temp_dir, "temp_concatenated.mp4")
            
            # Try FFmpeg concatenation first, fallback to MoviePy
            success = self.concatenate_videos_ffmpeg_with_progress(normalized_paths, temp_concat_path, progress_callback)
            
            if not success:
                self.logger.warning("FFmpeg concatenation failed, trying MoviePy")
                success = self.concatenate_videos_moviepy_with_progress(normalized_paths, temp_concat_path, progress_callback)
            
            if not success:
                self.logger.error("Video concatenation failed")
                return False
            
            # Update progress for trimming phase
            if progress_callback:
                progress_callback(1, 1, "trimming")
            
            # Check if we need to trim to exact duration
            concat_duration = self.get_video_duration(temp_concat_path)
            
            if concat_duration > target_duration:
                self.logger.info(f"DURATION CONTROL: Trimming video from {concat_duration:.1f}s to {target_duration}s")
                success = self.trim_video_to_duration(temp_concat_path, output_path, target_duration)
            else:
                # Duration is already correct or shorter, just copy the file
                import shutil
                shutil.copy2(temp_concat_path, output_path)
                success = True
            
            if success:
                final_duration = self.get_video_duration(output_path)
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                self.logger.pipeline_step("Video Processing Complete", 
                                        f"Final video: {final_duration:.1f}s (target: {target_duration}s), {file_size_mb:.1f}MB")
                self.logger.file_operation("Created", os.path.basename(output_path), f"{file_size_mb:.1f}MB")
                
                # Final progress update
                if progress_callback:
                    progress_callback(1, 1, "complete")
                
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
"""
Pexels API client for Background Video Generator.
Handles searching and downloading video clips from Pexels.
"""

import requests
import time
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import hashlib

class PexelsAPI:
    """Pexels API client for video operations."""
    
    def __init__(self, logger):
        """Initialize Pexels API client."""
        self.logger = logger
        self.base_url = "https://api.pexels.com/videos"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BackgroundVideoGenerator/1.0'
        })
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for authentication."""
        self.session.headers.update({
            'Authorization': api_key
        })
        self.logger.info("API: API key set successfully")
    
    def search_videos(self, query: str, per_page: int = 15, page: int = 1) -> Optional[Dict[str, Any]]:
        """Search for videos on Pexels."""
        try:
            self.logger.pipeline_step("API Search", f"Searching for '{query}' with {per_page} results per page")
            start_time = time.time()
            
            params = {
                'query': query,
                'per_page': per_page,
                'page': page
            }
            
            response = self.session.get(f"{self.base_url}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                elapsed = (time.time() - start_time) * 1000
                self.logger.performance(f"Pexels API Search completed in {elapsed:.0f}ms - Found {len(data.get('videos', []))} clips")
                self.logger.api_call("search", "SUCCESS", f"Query: {query}, Results: {len(data.get('videos', []))}")
                return data
            else:
                self.logger.error(f"API search failed with status {response.status_code}: {response.text}")
                self.logger.api_call("search", "FAILED", f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.exception(e, "API search")
            return None
    
    def get_video_files(self, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract video file information from video data."""
        video_files = video_data.get('video_files', [])
        return sorted(video_files, key=lambda x: x.get('width', 0), reverse=True)
    
    def filter_videos_by_duration(self, videos: List[Dict[str, Any]], min_duration: int, max_duration: int) -> List[Dict[str, Any]]:
        """Filter videos by duration range."""
        filtered = []
        for video in videos:
            duration = video.get('duration', 0)
            if min_duration <= duration <= max_duration:
                filtered.append(video)
        
        self.logger.info(f"VIDEO FILTERING: Filtered {len(videos)} videos to {len(filtered)} videos (duration {min_duration}-{max_duration}s)")
        return filtered
    
    def filter_videos_by_aspect_ratio(self, videos: List[Dict[str, Any]], aspect_ratio: str) -> List[Dict[str, Any]]:
        """Filter videos by aspect ratio preference."""
        filtered = []
        for video in videos:
            width = video.get('width', 0)
            height = video.get('height', 0)
            
            if width == 0 or height == 0:
                continue
                
            ratio = width / height
            
            if aspect_ratio == "horizontal" and ratio >= 1.5:
                filtered.append(video)
            elif aspect_ratio == "vertical" and ratio <= 0.75:
                filtered.append(video)
            elif aspect_ratio == "square" and 0.8 <= ratio <= 1.2:
                filtered.append(video)
        
        self.logger.info(f"VIDEO FILTERING: Filtered to {len(filtered)} videos with {aspect_ratio} aspect ratio")
        return filtered
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """Download a video file."""
        try:
            self.logger.file_operation("Downloading", os.path.basename(output_path))
            start_time = time.time()
            
            response = self.session.get(video_url, stream=True)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            elapsed = time.time() - start_time
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            if total_size > 0:
                speed_mbps = (file_size_mb / elapsed) if elapsed > 0 else 0
                self.logger.performance(f"Download completed in {elapsed:.1f}s - {file_size_mb:.1f}MB at {speed_mbps:.1f}MB/s")
            else:
                self.logger.performance(f"Download completed in {elapsed:.1f}s - {file_size_mb:.1f}MB")
            
            self.logger.file_operation("Downloaded", os.path.basename(output_path), f"{file_size_mb:.1f}MB")
            return True
            
        except Exception as e:
            self.logger.exception(e, f"Downloading {video_url}")
            return False
    
    def get_best_video_url(self, video_files: List[Dict[str, Any]], target_resolution: str) -> Optional[str]:
        """Get the best video URL for the target resolution."""
        target_width, target_height = map(int, target_resolution.split('x'))
        
        # Sort by resolution quality (closest to target)
        def quality_score(video_file):
            width = video_file.get('width', 0)
            height = video_file.get('height', 0)
            
            if width == 0 or height == 0:
                return float('inf')
            
            # Calculate distance from target resolution
            width_diff = abs(width - target_width)
            height_diff = abs(height - target_height)
            return width_diff + height_diff
        
        sorted_files = sorted(video_files, key=quality_score)
        
        if sorted_files:
            best_file = sorted_files[0]
            self.logger.info(f"VIDEO SELECTION: Selected {best_file.get('width')}x{best_file.get('height')} video")
            return best_file.get('link')
        
        return None
    
    def search_and_download_videos(self, query: str, target_duration: int, target_resolution: str, 
                                 aspect_ratio: str, max_clips: int, min_clip_duration: int, 
                                 max_clip_duration: int, output_dir: str) -> List[str]:
        """Search for videos and download them."""
        try:
            self.logger.pipeline_step("Video Search and Download", f"Query: {query}, Target: {target_duration}s")
            
            # Search for videos
            search_result = self.search_videos(query, per_page=80)  # Get more results for filtering
            if not search_result:
                self.logger.error("No search results returned")
                return []
            
            videos = search_result.get('videos', [])
            if not videos:
                self.logger.warning(f"No videos found for query: {query}")
                return []
            
            # Filter videos by duration
            filtered_videos = self.filter_videos_by_duration(videos, min_clip_duration, max_clip_duration)
            
            # Filter by aspect ratio
            filtered_videos = self.filter_videos_by_aspect_ratio(filtered_videos, aspect_ratio)
            
            if not filtered_videos:
                self.logger.warning("No videos match the filtering criteria")
                return []
            
            # Limit to max_clips
            selected_videos = filtered_videos[:max_clips]
            
            # Download videos
            downloaded_files = []
            for i, video in enumerate(selected_videos):
                video_files = self.get_video_files(video)
                video_url = self.get_best_video_url(video_files, target_resolution)
                
                if video_url:
                    # Create filename based on video ID and query
                    video_id = video.get('id', i)
                    filename = f"clip_{i}_{video_id}_{query.replace(' ', '_')}.mp4"
                    output_path = os.path.join(output_dir, filename)
                    
                    if self.download_video(video_url, output_path):
                        downloaded_files.append(output_path)
                        self.logger.info(f"VIDEO DOWNLOAD: Successfully downloaded clip {i+1}/{len(selected_videos)}")
                    else:
                        self.logger.error(f"VIDEO DOWNLOAD: Failed to download clip {i+1}")
                else:
                    self.logger.warning(f"VIDEO DOWNLOAD: No suitable video URL found for clip {i+1}")
            
            self.logger.pipeline_step("Video Download Complete", f"Downloaded {len(downloaded_files)} clips")
            return downloaded_files
            
        except Exception as e:
            self.logger.exception(e, "Video search and download")
            return [] 
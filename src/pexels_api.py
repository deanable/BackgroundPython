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
    
    def calculate_optimal_clip_count(self, target_duration: int, min_clip_duration: int, max_clip_duration: int, max_clips: int) -> int:
        """Calculate optimal number of clips needed based on target duration."""
        # Estimate average clip duration
        avg_clip_duration = (min_clip_duration + max_clip_duration) / 2
        
        # Calculate how many clips we'd need to reach target duration
        estimated_clips_needed = int(target_duration / avg_clip_duration) + 2  # Add buffer
        
        # Don't exceed max_clips, but ensure we get enough for longer videos
        optimal_clips = min(max(estimated_clips_needed, 5), max_clips)  # At least 5 clips, max as configured
        
        self.logger.info(f"CLIP CALCULATION: Target {target_duration}s, avg clip {avg_clip_duration:.1f}s, requesting {optimal_clips} clips")
        return optimal_clips

    def analyze_available_content(self, query: str, aspect_ratio: str) -> Dict[str, Any]:
        """Analyze available content for a query to provide smart duration recommendations."""
        try:
            self.logger.info(f"CONTENT ANALYSIS: Analyzing available content for '{query}'")
            
            # Search multiple pages to get comprehensive results
            all_videos = []
            page = 1
            max_pages = 3  # Limit for analysis
            
            while page <= max_pages:
                search_result = self.search_videos(query, per_page=80, page=page)
                if not search_result:
                    break
                    
                videos = search_result.get('videos', [])
                if not videos:
                    break
                    
                all_videos.extend(videos)
                page += 1
            
            if not all_videos:
                return {
                    'total_clips': 0,
                    'total_duration': 0,
                    'filtered_clips': 0,
                    'filtered_duration': 0,
                    'duration_range': {'min': 0, 'max': 0},
                    'recommended_max_duration': 0,
                    'clips_by_duration': {}
                }
            
            # Remove duplicates
            unique_videos = []
            seen_ids = set()
            for video in all_videos:
                video_id = video.get('id')
                if video_id not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video_id)
            
            # Filter by aspect ratio
            filtered_videos = self.filter_videos_by_aspect_ratio(unique_videos, aspect_ratio)
            
            # Analyze duration distribution
            durations = []
            clips_by_duration = {'short': 0, 'medium': 0, 'long': 0}  # <15s, 15-45s, >45s
            
            for video in filtered_videos:
                duration = video.get('duration', 0)
                if duration > 0:
                    durations.append(duration)
                    if duration < 15:
                        clips_by_duration['short'] += 1
                    elif duration <= 45:
                        clips_by_duration['medium'] += 1
                    else:
                        clips_by_duration['long'] += 1
            
            total_available_duration = sum(durations)
            
            # Calculate recommendations
            if durations:
                min_duration = min(durations)
                max_duration = max(durations)
                avg_duration = total_available_duration / len(durations)
                
                # Recommend maximum duration that won't require repetition
                recommended_max = total_available_duration * 0.9  # 90% to account for processing
            else:
                min_duration = max_duration = avg_duration = recommended_max = 0
            
            analysis = {
                'total_clips': len(unique_videos),
                'total_duration': sum(video.get('duration', 0) for video in unique_videos),
                'filtered_clips': len(filtered_videos),
                'filtered_duration': total_available_duration,
                'duration_range': {
                    'min': min_duration,
                    'max': max_duration,
                    'avg': avg_duration
                },
                'recommended_max_duration': recommended_max,
                'clips_by_duration': clips_by_duration,
                'aspect_ratio': aspect_ratio
            }
            
            self.logger.info(f"CONTENT ANALYSIS: Found {len(filtered_videos)} clips, {total_available_duration:.1f}s total duration")
            return analysis
            
        except Exception as e:
            self.logger.exception(e, "Content analysis")
            return {
                'total_clips': 0,
                'total_duration': 0,
                'filtered_clips': 0,
                'filtered_duration': 0,
                'duration_range': {'min': 0, 'max': 0},
                'recommended_max_duration': 0,
                'clips_by_duration': {}
            }

    def search_multiple_pages(self, query: str, target_clips_needed: int) -> List[Dict[str, Any]]:
        """Search multiple pages to get enough clips without repetition."""
        all_videos = []
        page = 1
        max_pages = 5  # Limit to prevent infinite loops
        
        while len(all_videos) < target_clips_needed and page <= max_pages:
            self.logger.info(f"MULTI-PAGE SEARCH: Fetching page {page} for more clips")
            search_result = self.search_videos(query, per_page=80, page=page)
            
            if not search_result:
                break
                
            videos = search_result.get('videos', [])
            if not videos:
                break
                
            all_videos.extend(videos)
            page += 1
            
            # Stop if we have enough unique videos
            if len(all_videos) >= target_clips_needed * 2:  # Get extra for filtering
                break
        
        self.logger.info(f"MULTI-PAGE SEARCH: Collected {len(all_videos)} total clips from {page-1} pages")
        return all_videos

    def search_and_download_videos(self, query: str, target_duration: int, target_resolution: str, 
                                 aspect_ratio: str, max_clips: int, min_clip_duration: int, 
                                 max_clip_duration: int, output_dir: str) -> List[str]:
        """Search for videos and download them with intelligent clip selection to avoid repetition."""
        try:
            self.logger.pipeline_step("Video Search and Download", f"Query: {query}, Target: {target_duration}s")
            
            # Calculate optimal number of clips to download
            optimal_clip_count = self.calculate_optimal_clip_count(target_duration, min_clip_duration, max_clip_duration, max_clips)
            
            # Search multiple pages if needed to get enough unique clips
            all_videos = self.search_multiple_pages(query, optimal_clip_count)
            
            if not all_videos:
                self.logger.error("No search results returned")
                return []
            
            # Filter videos by duration with more relaxed criteria for longer videos
            if target_duration > 600:  # For videos longer than 10 minutes, be more flexible
                # Expand duration range to get more clips
                expanded_min = max(5, min_clip_duration - 5)  # Allow slightly shorter clips
                expanded_max = min(60, max_clip_duration + 15)  # Allow longer clips
                self.logger.info(f"EXPANDED FILTERING: Using duration range {expanded_min}-{expanded_max}s for longer target video")
                filtered_videos = self.filter_videos_by_duration(all_videos, expanded_min, expanded_max)
            else:
                filtered_videos = self.filter_videos_by_duration(all_videos, min_clip_duration, max_clip_duration)
            
            # Filter by aspect ratio
            filtered_videos = self.filter_videos_by_aspect_ratio(filtered_videos, aspect_ratio)
            
            if not filtered_videos:
                self.logger.warning("No videos match the filtering criteria")
                return []
            
            # Remove duplicates based on video ID
            unique_videos = []
            seen_ids = set()
            for video in filtered_videos:
                video_id = video.get('id')
                if video_id not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video_id)
            
            self.logger.info(f"DEDUPLICATION: Removed duplicates, {len(unique_videos)} unique clips available")
            
            # Select clips - prioritize getting enough unique clips
            clips_needed = min(optimal_clip_count, len(unique_videos))
            selected_videos = unique_videos[:clips_needed]
            
            # Calculate estimated total duration of selected clips
            estimated_total_duration = 0
            for video in selected_videos:
                estimated_total_duration += video.get('duration', max_clip_duration)
            
            self.logger.info(f"CLIP SELECTION: Selected {len(selected_videos)} unique clips with estimated total duration {estimated_total_duration:.1f}s")
            
            # If we still don't have enough duration, warn but proceed
            if estimated_total_duration < target_duration * 0.8:  # Less than 80% of target
                self.logger.warning(f"INSUFFICIENT CLIPS: Only {estimated_total_duration:.1f}s available for {target_duration}s target. Video may be shorter than requested or require minimal repetition.")
            
            # Download videos
            downloaded_files = []
            for i, video in enumerate(selected_videos):
                video_files = self.get_video_files(video)
                video_url = self.get_best_video_url(video_files, target_resolution)
                
                if video_url:
                    # Create filename with temp prefix for better cleanup
                    video_id = video.get('id', i)
                    filename = f"temp_background_video_clip_{i}_{video_id}_{query.replace(' ', '_')}.mp4"
                    output_path = os.path.join(output_dir, filename)
                    
                    if self.download_video(video_url, output_path):
                        downloaded_files.append(output_path)
                        self.logger.info(f"VIDEO DOWNLOAD: Successfully downloaded clip {i+1}/{len(selected_videos)}")
                    else:
                        self.logger.error(f"VIDEO DOWNLOAD: Failed to download clip {i+1}")
                else:
                    self.logger.warning(f"VIDEO DOWNLOAD: No suitable video URL found for clip {i+1}")
            
            self.logger.pipeline_step("Video Download Complete", f"Downloaded {len(downloaded_files)} unique clips")
            return downloaded_files
            
        except Exception as e:
            self.logger.exception(e, "Video search and download")
            return []

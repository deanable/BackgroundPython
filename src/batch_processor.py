"""
Batch video processing manager with queue and parallel processing support.
"""

import os
import threading
import queue
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from src.video_processor_enhanced import EnhancedVideoProcessor

class BatchProcessor:
    """Manages batch video processing with queue and parallel execution."""
    
    def __init__(self, logger, max_workers: int = 2):
        """Initialize batch processor."""
        self.logger = logger
        self.processor = EnhancedVideoProcessor(logger)
        self.max_workers = max_workers
        self.processing_queue = queue.Queue()
        self.results = {}
        self.is_running = False
        
    def add_job(self, job_id: str, video_paths: List[str], target_duration: int, 
                output_path: str, preset: str = "presentation", 
                progress_callback: Optional[Callable] = None) -> None:
        """Add a processing job to the queue."""
        job = {
            'id': job_id,
            'video_paths': video_paths,
            'target_duration': target_duration,
            'output_path': output_path,
            'preset': preset,
            'progress_callback': progress_callback,
            'status': 'queued',
            'start_time': None,
            'end_time': None
        }
        
        self.processing_queue.put(job)
        self.results[job_id] = job
        
    def process_batch(self) -> Dict[str, Any]:
        """Process all jobs in the queue with parallel execution."""
        if self.is_running:
            return {"error": "Batch processing already running"}
        
        self.is_running = True
        jobs = []
        
        # Collect all jobs from queue
        while not self.processing_queue.empty():
            try:
                job = self.processing_queue.get_nowait()
                jobs.append(job)
            except queue.Empty:
                break
        
        if not jobs:
            return {"error": "No jobs to process"}
        
        # Process jobs in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_job = {
                executor.submit(self._process_single_job, job): job 
                for job in jobs
            }
            
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    result = future.result()
                    self.results[job['id']].update(result)
                except Exception as e:
                    self.logger.exception(e, f"Processing job {job['id']}")
                    self.results[job['id']].update({
                        'status': 'failed',
                        'error': str(e)
                    })
        
        self.is_running = False
        return self.results
    
    def _process_single_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single job."""
        job['status'] = 'processing'
        job['start_time'] = time.time()
        
        try:
            success = self.processor.process_with_preset(
                video_paths=job['video_paths'],
                preset_name=job['preset'],
                target_duration=job['target_duration'],
                output_path=job['output_path'],
                progress_callback=job['progress_callback']
            )
            
            job['status'] = 'completed' if success else 'failed'
            job['end_time'] = time.time()
            job['duration'] = job['end_time'] - job['start_time']
            
            return job
            
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['end_time'] = time.time()
            return job
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        return self.results.get(job_id)
    
    def get_all_statuses(self) -> Dict[str, Any]:
        """Get status of all jobs."""
        return self.results
    
    def clear_completed_jobs(self) -> None:
        """Clear completed jobs from results."""
        self.results = {
            job_id: job for job_id, job in self.results.items()
            if job['status'] not in ['completed', 'failed']
        }

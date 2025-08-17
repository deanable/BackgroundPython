"""
Example usage of the enhanced video processing pipeline.
"""

import os
import sys
from typing import List, Dict, Any
from src.logger import Logger
from src.video_processor_enhanced import EnhancedVideoProcessor
from src.batch_processor import BatchProcessor
from src.quality_assessor import QualityAssessor

def example_single_video_processing():
    """Example: Process a single video with quality assessment."""
    logger = Logger()
    
    # Initialize components
    processor = EnhancedVideoProcessor(logger)
    assessor = QualityAssessor(logger)
    
    # Example video paths
    video_paths = ["input/video1.mp4", "input/video2.mp4"]
    output_path = "output/processed_video.mp4"
    target_duration = 60  # 60 seconds
    
    # Process video
    success = processor.process_with_preset(
        video_paths=video_paths,
        preset_name="social_media",
        target_duration=target_duration,
        output_path=output_path
    )
    
    if success:
        # Assess quality
        quality_report = assessor.assess_video_quality(output_path)
        print("Quality Assessment:", quality_report)
        
        # Validate integrity
        is_valid = assessor.validate_video_integrity(output_path)
        print(f"Video integrity: {'Valid' if is_valid else 'Invalid'}")

def example_batch_processing():
    """Example: Process multiple videos in batch."""
    logger = Logger()
    batch_processor = BatchProcessor(logger, max_workers=2)
    
    # Define batch jobs
    jobs = [
        {
            "id": "job1",
            "video_paths": ["input/video1.mp4", "input/video2.mp4"],
            "target_duration": 30,
            "output_path": "output/batch1.mp4",
            "preset": "social_media"
        },
        {
            "id": "job2",
            "video_paths": ["input/video3.mp4", "input/video4.mp4"],
            "target_duration": 45,
            "output_path": "output/batch2.mp4",
            "preset": "presentation"
        }
    ]
    
    # Add jobs to queue
    for job in jobs:
        batch_processor.add_job(
            job_id=job["id"],
            video_paths=job["video_paths"],
            target_duration=job["target_duration"],
            output_path=job["output_path"],
            preset=job["preset"]
        )
    
    # Process all jobs
    results = batch_processor.process_batch()
    
    # Print results
    for job_id, result in results.items():
        print(f"Job {job_id}: {result['status']}")
        if result['status'] == 'completed':
            print(f"  Duration: {result['duration']:.2f}s")

def example_quality_comparison():
    """Example: Compare original vs processed video quality."""
    logger = Logger()
    assessor = QualityAssessor(logger)
    
    original_path = "input/original_video.mp4"
    processed_path = "output/processed_video.mp4"
    
    # Compare videos
    comparison = assessor.compare_videos(original_path, processed_path)
    
    print("Quality Comparison:")
    print(f"Original Overall Score: {comparison['original']['quality_scores']['overall_score']:.2f}")
    print(f"Processed Overall Score: {comparison['processed']['quality_scores']['overall_score']:.2f}")
    
    for score_type, change in comparison['quality_change'].items():
        print(f"{score_type}: {'+' if change > 0 else ''}{change:.2f}")

def example_intelligent_duration_control():
    """Example: Use intelligent duration extension."""
    logger = Logger()
    processor = EnhancedVideoProcessor(logger)
    
    video_paths = ["input/clip1.mp4", "input/clip2.mp4", "input/clip3.mp4"]
    target_duration = 120  # 2 minutes
    
    # Use intelligent extension
    extended_paths = processor.intelligent_duration_extension(
        video_paths=video_paths,
        target_duration=target_duration,
        min_clip_duration=2
    )
    
    print(f"Original clips: {len(video_paths)}")
    print(f"Extended clips: {len(extended_paths)}")
    print(f"Total duration: {target_duration}s")

def create_processing_report(output_dir: str) -> Dict[str, Any]:
    """Create a comprehensive processing report."""
    logger = Logger()
    assessor = QualityAssessor(logger)
    
    report = {
        "processing_summary": {},
        "quality_metrics": {},
        "recommendations": []
    }
    
    # Scan output directory
    processed_videos = []
    for file in os.listdir(output_dir):
        if file.endswith(('.mp4', '.avi', '.mov')):
            processed_videos.append(os.path.join(output_dir, file))
    
    # Analyze each video
    for video_path in processed_videos:
        quality = assessor.assess_video_quality(video_path)
        report["quality_metrics"][os.path.basename(video_path)] = quality
    
    # Generate summary
    total_videos = len(processed_videos)
    avg_quality = sum(
        q["quality_scores"]["overall_score"] 
        for q in report["quality_metrics"].values()
        if "quality_scores" in q
    ) / total_videos if total_videos > 0 else 0
    
    report["processing_summary"] = {
        "total_videos": total_videos,
        "average_quality": avg_quality,
        "output_directory": output_dir
    }
    
    # Save report
    report_path = os.path.join(output_dir, "processing_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Run examples
    print("=== Video Processing Pipeline Examples ===")
    
    # Example 1: Single video processing
    print("\n1. Single Video Processing")
    example_single_video_processing()
    
    # Example 2: Batch processing
    print("\n2. Batch Processing")
    example_batch_processing()
    
    # Example 3: Quality comparison
    print("\n3. Quality Comparison")
    example_quality_comparison()
    
    # Example 4: Intelligent duration control
    print("\n4. Intelligent Duration Control")
    example_intelligent_duration_control()
    
    # Example 5: Create processing report
    print("\n5. Processing Report")
    report = create_processing_report("output")
    print(f"Report saved to: output/processing_report.json")

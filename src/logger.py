"""
Advanced logging system for Background Video Generator.
Provides comprehensive logging with different levels and categories.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

class AdvancedLogger:
    """Advanced logging system with categorized logging."""
    
    def __init__(self):
        """Initialize the advanced logger."""
        self.start_time = time.time()
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Remove default logger
        logger.remove()
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup file logging
        log_file = f"logs/log-{self.session_id}.log"
        logger.add(
            log_file,
            format="[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{elapsed}] [{level: <8}] {message}",
            level="DEBUG",
            rotation=None,
            compression=None,
            backtrace=True,
            diagnose=True
        )
        
        # Setup console logging
        logger.add(
            sys.stdout,
            format="[{time:HH:mm:ss}] [{level: <8}] {message}",
            level="INFO",
            colorize=True
        )
        
        self.logger = logger
    
    def get_session_time(self) -> str:
        """Get elapsed session time."""
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def debug(self, message: str, category: str = "GENERAL") -> None:
        """Log debug message."""
        self.logger.debug(f"{category}: {message}")
    
    def info(self, message: str, category: str = "GENERAL") -> None:
        """Log info message."""
        self.logger.info(f"{category}: {message}")
    
    def warning(self, message: str, category: str = "GENERAL") -> None:
        """Log warning message."""
        self.logger.warning(f"{category}: {message}")
    
    def error(self, message: str, category: str = "GENERAL") -> None:
        """Log error message."""
        self.logger.error(f"{category}: {message}")
    
    def critical(self, message: str, category: str = "GENERAL") -> None:
        """Log critical message."""
        self.logger.critical(f"{category}: {message}")
    
    def performance(self, message: str) -> None:
        """Log performance metric."""
        self.logger.info(f"PERFORMANCE: {message}")
    
    def pipeline_step(self, step: str, details: str = "") -> None:
        """Log pipeline step."""
        message = f"PIPELINE STEP: {step}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def api_call(self, endpoint: str, status: str, details: str = "") -> None:
        """Log API call."""
        message = f"API CALL: {endpoint} - {status}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def file_operation(self, operation: str, filename: str, details: str = "") -> None:
        """Log file operation."""
        message = f"FILE OPERATION: {operation} - {filename}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def video_processing(self, operation: str, input_file: str, output_file: str = "", details: str = "") -> None:
        """Log video processing operation."""
        message = f"VIDEO PROCESSING: {operation} - {input_file}"
        if output_file:
            message += f" -> {output_file}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def system_info(self, info_type: str, details: str) -> None:
        """Log system information."""
        self.logger.info(f"SYSTEM: {info_type} - {details}")
    
    def exception(self, exception: Exception, context: str = "") -> None:
        """Log exception with context."""
        message = f"EXCEPTION: {type(exception).__name__}: {str(exception)}"
        if context:
            message += f" - Context: {context}"
        self.logger.exception(message)

def setup_logger() -> AdvancedLogger:
    """Setup and return the advanced logger instance."""
    return AdvancedLogger() 
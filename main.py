#!/usr/bin/env python3
"""
Background Video Generator - Main Application
A Python application for creating background videos from Pexels clips.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from src.gui import BackgroundVideoGUI
from src.config import Config
from src.logger import setup_logger
from src.video_processor import VideoProcessor
from src.pexels_api import PexelsAPI

class BackgroundVideoGenerator:
    """Main application class for the Background Video Generator."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.logger = setup_logger()
        self.video_processor = VideoProcessor(self.logger)
        self.pexels_api = PexelsAPI(self.logger)
        
        self.logger.info("APPLICATION: Background Video Generator starting up")
        self.logger.info(f"SYSTEM: Python version {sys.version}")
        self.logger.info(f"SYSTEM: Operating system {os.name}")
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize GUI
        self.root = tk.Tk()
        self.gui = BackgroundVideoGUI(
            self.root, 
            self.config, 
            self.video_processor, 
            self.pexels_api,
            self.logger
        )
        
        self.logger.info("APPLICATION: GUI initialized successfully")
    
    def run(self):
        """Run the application."""
        try:
            self.logger.info("APPLICATION: Starting main application loop")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"APPLICATION: Critical error in main loop: {e}")
            messagebox.showerror("Error", f"Critical application error: {e}")
        finally:
            self.logger.info("APPLICATION: Application shutting down")
    
    def cleanup(self):
        """Clean up resources before exit."""
        self.logger.info("APPLICATION: Performing cleanup")
        if hasattr(self, 'video_processor'):
            self.video_processor.cleanup()

def main():
    """Main entry point for the application."""
    app = None
    try:
        app = BackgroundVideoGenerator()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        if app and hasattr(app, 'logger'):
            app.logger.error(f"APPLICATION: Fatal error: {e}")
    finally:
        if app:
            app.cleanup()

if __name__ == "__main__":
    main() 
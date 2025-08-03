"""
GUI module for Background Video Generator.
Provides a user-friendly interface for video generation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class BackgroundVideoGUI:
    """GUI class for Background Video Generator."""
    
    def __init__(self, root, config, video_processor, pexels_api, logger):
        """Initialize the GUI."""
        self.root = root
        self.config = config
        self.video_processor = video_processor
        self.pexels_api = pexels_api
        self.logger = logger
        
        self.processing = False
        self.progress_var = tk.DoubleVar()
        
        self.setup_window()
        self.create_widgets()
        self.load_config()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """Setup the main window."""
        self.root.title("Background Video Generator")
        self.root.geometry(self.config.get_window_geometry())
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(600, 500)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Background Video Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # API Key Section
        api_frame = ttk.LabelFrame(main_frame, text="Pexels API Configuration", padding="10")
        api_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Search Configuration Section
        search_frame = ttk.LabelFrame(main_frame, text="Video Search Configuration", padding="10")
        search_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search term
        ttk.Label(search_frame, text="Search Term:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_term_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_term_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
                # Duration
        ttk.Label(search_frame, text="Target Duration (minutes):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.duration_var = tk.IntVar()
        target_duration_slider = ttk.Scale(search_frame, from_=1, to=60, variable=self.duration_var, 
                                            orient='horizontal', length=200)
        target_duration_slider.grid(row=1, column=1, columnspan=2, sticky='ew')
        self.duration_label = ttk.Label(search_frame, text="5")
        self.duration_label.grid(row=1, column=3, sticky=tk.W)
        
        # Update duration label when slider changes
        def update_duration_label(*args):
            self.duration_label.config(text=str(int(self.duration_var.get())))
        self.duration_var.trace('w', update_duration_label)
        
        # Resolution
        ttk.Label(search_frame, text="Resolution:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.resolution_var = tk.StringVar()
        resolution_combo = ttk.Combobox(search_frame, textvariable=self.resolution_var, 
                                       values=["1920x1080", "3840x2160", "1280x720"], 
                                       state="readonly", width=15)
        resolution_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 10))
        
        # Aspect ratio
        ttk.Label(search_frame, text="Aspect Ratio:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.aspect_ratio_var = tk.StringVar()
        aspect_combo = ttk.Combobox(search_frame, textvariable=self.aspect_ratio_var,
                                   values=["horizontal", "vertical", "square"],
                                   state="readonly", width=15)
        aspect_combo.grid(row=3, column=1, sticky=tk.W, padx=(0, 10))
        
        # Advanced Settings Section
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Settings", padding="10")
        advanced_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Max clips
        ttk.Label(advanced_frame, text="Max Clips:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.max_clips_var = tk.IntVar()
        max_clips_spinbox = ttk.Spinbox(advanced_frame, from_=1, to=50, textvariable=self.max_clips_var, width=10)
        max_clips_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Min clip duration
        ttk.Label(advanced_frame, text="Min Clip Duration (s):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.min_clip_duration_var = tk.IntVar()
        min_duration_slider = ttk.Scale(advanced_frame, from_=1, to=60, variable=self.min_clip_duration_var,
                                        orient='horizontal', length=200)
        min_duration_slider.grid(row=1, column=1, columnspan=2, sticky='ew')
        self.min_duration_label = ttk.Label(advanced_frame, text="1")
        self.min_duration_label.grid(row=1, column=3, sticky=tk.W)
        
        # Update min duration label when slider changes
        def update_min_duration_label(*args):
            self.min_duration_label.config(text=str(int(self.min_clip_duration_var.get())))
        self.min_clip_duration_var.trace('w', update_min_duration_label)
        
        # Max clip duration
        ttk.Label(advanced_frame, text="Max Clip Duration (s):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.max_clip_duration_var = tk.IntVar()
        max_duration_slider = ttk.Scale(advanced_frame, from_=5, to=300, variable=self.max_clip_duration_var,
                                        orient='horizontal', length=200)
        max_duration_slider.grid(row=2, column=1, columnspan=2, sticky='ew')
        self.max_duration_label = ttk.Label(advanced_frame, text="5")
        self.max_duration_label.grid(row=2, column=3, sticky=tk.W)
        
        # Update max duration label when slider changes
        def update_max_duration_label(*args):
            self.max_duration_label.config(text=str(int(self.max_clip_duration_var.get())))
        self.max_clip_duration_var.trace('w', update_max_duration_label)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Configuration", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, padx=(10, 0))
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Generation", command=self.start_generation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_generation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Open Logs", command=self.open_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", command=self.on_closing).pack(side=tk.LEFT)
    
    def load_config(self):
        """Load configuration values into GUI."""
        self.api_key_var.set(self.config.get_api_key())
        self.search_term_var.set(self.config.get_search_term())
        # Convert target duration from seconds to minutes for UI display
        self.duration_var.set(self.config.get_duration() // 60)
        self.resolution_var.set(self.config.get_resolution())
        self.aspect_ratio_var.set(self.config.get_aspect_ratio())
        self.max_clips_var.set(self.config.get_max_clips())
        # Keep clip durations in seconds
        self.min_clip_duration_var.set(self.config.get_min_clip_duration())
        self.max_clip_duration_var.set(self.config.get_max_clip_duration())
        self.output_dir_var.set(self.config.get_output_dir())
        
        # Update labels to show integer values
        self.root.after(100, self.update_slider_labels)
    
    def update_slider_labels(self):
        """Update slider labels to show integer values."""
        self.duration_label.config(text=str(int(self.duration_var.get())))
        self.min_duration_label.config(text=str(int(self.min_clip_duration_var.get())))
        self.max_duration_label.config(text=str(int(self.max_clip_duration_var.get())))
    
    def save_config(self):
        """Save GUI values to configuration."""
        self.config.set_api_key(self.api_key_var.get())
        self.config.set_search_term(self.search_term_var.get())
        self.config.set_duration(self.duration_var.get() * 60)
        self.config.set_resolution(self.resolution_var.get())
        self.config.set_aspect_ratio(self.aspect_ratio_var.get())
        self.config.set_max_clips(self.max_clips_var.get())
        self.config.set_min_clip_duration(self.min_clip_duration_var.get())
        self.config.set_max_clip_duration(self.max_clip_duration_var.get())
        self.config.set_output_dir(self.output_dir_var.get())
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        if not self.api_key_var.get().strip():
            messagebox.showerror("Error", "Please enter your Pexels API key")
            return False
        
        if not self.search_term_var.get().strip():
            messagebox.showerror("Error", "Please enter a search term")
            return False
        
        if not self.output_dir_var.get().strip():
            messagebox.showerror("Error", "Please select an output directory")
            return False
        
        if not os.path.exists(self.output_dir_var.get()):
            messagebox.showerror("Error", "Output directory does not exist")
            return False
        
        return True
    
    def start_generation(self):
        """Start the video generation process."""
        if not self.validate_inputs():
            return
        
        self.save_config()
        
        # Set up API
        self.pexels_api.set_api_key(self.api_key_var.get())
        
        # Update UI state
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.generate_video_thread)
        thread.daemon = True
        thread.start()
    
    def generate_video_thread(self):
        """Background thread for video generation."""
        try:
            self.logger.pipeline_step("Video Generation Started", "User initiated generation")
            
            # Get parameters
            search_term = self.search_term_var.get()
            target_duration = self.duration_var.get() * 60
            target_resolution = self.resolution_var.get()
            aspect_ratio = self.aspect_ratio_var.get()
            max_clips = self.max_clips_var.get()
            min_clip_duration = self.min_clip_duration_var.get()
            max_clip_duration = self.max_clip_duration_var.get()
            output_dir = self.output_dir_var.get()
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"background_video_{search_term.replace(' ', '_')}_{timestamp}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            # Update status for downloading phase (0-50%)
            self.root.after(0, lambda: self.status_var.set("Searching and downloading videos..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Search and download videos
            downloaded_files = self.pexels_api.search_and_download_videos(
                search_term, target_duration, target_resolution, aspect_ratio,
                max_clips, min_clip_duration, max_clip_duration, output_dir
            )
            
            if not downloaded_files:
                self.root.after(0, lambda: messagebox.showerror("Error", "No videos were downloaded"))
                return
            
            # Update status for processing phase (50-100%)
            self.root.after(0, lambda: self.status_var.set("Processing and concatenating videos..."))
            self.root.after(0, lambda: self.progress_var.set(50))
            
            # Process videos with progress callback
            def progress_callback(current_file, total_files, current_step):
                """Callback to update progress during video processing."""
                if total_files > 0:
                    if current_step == "normalizing":
                        # Normalization stage: 50-75%
                        file_progress = (current_file / total_files) * 0.25  # 0.25 = 25% of total progress
                        total_progress = 50 + file_progress  # Start from 50%
                        status_text = f"Normalizing video {current_file}/{total_files}..."
                    elif current_step == "concatenating":
                        # Concatenation stage: 75-100%
                        file_progress = (current_file / total_files) * 0.25  # 0.25 = 25% of total progress
                        total_progress = 75 + file_progress  # Start from 75%
                        status_text = f"Concatenating videos ({current_file}/{total_files})..."
                    else:
                        # Fallback
                        file_progress = (current_file / total_files) * 0.5
                        total_progress = 50 + file_progress
                        status_text = f"Processing video {current_file}/{total_files}..."
                    
                    self.root.after(0, lambda: self.progress_var.set(total_progress))
                    self.root.after(0, lambda: self.status_var.set(status_text))
            
            # Process videos with progress callback
            success = self.video_processor.process_videos_with_progress(
                downloaded_files, target_duration, target_resolution, output_path, progress_callback
            )
            
            if success:
                self.root.after(0, lambda: self.status_var.set("Video generation completed!"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Video generated successfully!\nOutput: {output_path}"))
                
                # Clean up downloaded files
                for file_path in downloaded_files:
                    try:
                        os.remove(file_path)
                        self.logger.file_operation("Cleaned up", os.path.basename(file_path))
                    except Exception as e:
                        self.logger.warning(f"Failed to clean up {file_path}: {e}")
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Video processing failed. Check logs for details."))
            
        except Exception as e:
            self.logger.exception(e, "Video generation thread")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Video generation failed: {e}"))
        finally:
            # Reset UI state
            self.root.after(0, self.reset_ui_state)
    
    def stop_generation(self):
        """Stop the video generation process."""
        self.processing = False
        self.status_var.set("Stopping...")
        self.logger.info("USER: Video generation stopped by user")
    
    def reset_ui_state(self):
        """Reset UI to initial state."""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Ready")
    
    def open_logs(self):
        """Open the logs directory."""
        logs_dir = Path("logs")
        if logs_dir.exists():
            if os.name == 'nt':  # Windows
                os.startfile(logs_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{logs_dir}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{logs_dir}"')
        else:
            messagebox.showinfo("Info", "No logs directory found")
    
    def on_closing(self):
        """Handle window closing."""
        if self.processing:
            if messagebox.askokcancel("Quit", "Video generation is in progress. Do you want to quit?"):
                self.processing = False
                self.save_window_geometry()
                self.root.destroy()
        else:
            self.save_window_geometry()
            self.root.destroy()
    
    def save_window_geometry(self):
        """Save window geometry to configuration."""
        geometry = self.root.geometry()
        self.config.set_window_geometry(geometry) 
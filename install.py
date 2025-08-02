#!/usr/bin/env python3
"""
Installation script for Background Video Generator.
Helps users set up the application and check dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or later is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg check failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("❌ FFmpeg not found")
        print("   Please install FFmpeg from: https://ffmpeg.org/download.html")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    try:
        Path("logs").mkdir(exist_ok=True)
        print("✅ Created logs directory")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 Background Video Generator - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg is required but not found.")
        print("   The application may not work properly without FFmpeg.")
        print("   You can continue with installation and install FFmpeg later.")
        
        response = input("\nContinue with installation? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\nTo run the application:")
    print("   python main.py")
    print("\nMake sure to:")
    print("   1. Get a Pexels API key from: https://www.pexels.com/api/")
    print("   2. Install FFmpeg if not already installed")
    print("   3. Run the application and enter your API key")

if __name__ == "__main__":
    main() 
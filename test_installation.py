#!/usr/bin/env python3
"""
Test script for Background Video Generator.
Verifies that all components are working correctly.
"""

import sys
import os
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests")
        return False
    
    try:
        import cv2
        print("✅ opencv-python")
    except ImportError:
        print("❌ opencv-python")
        return False
    
    try:
        from moviepy.editor import VideoFileClip
        print("✅ moviepy")
    except ImportError:
        print("❌ moviepy")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow")
    except ImportError:
        print("❌ Pillow")
        return False
    
    try:
        from loguru import logger
        print("✅ loguru")
    except ImportError:
        print("❌ loguru")
        return False
    
    try:
        import tkinter
        print("✅ tkinter")
    except ImportError:
        print("❌ tkinter")
        return False
    
    return True

def test_ffmpeg():
    """Test FFmpeg availability."""
    print("\n🔍 Testing FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg check failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("❌ FFmpeg not found")
        return False

def test_application_modules():
    """Test if application modules can be imported."""
    print("\n🔍 Testing application modules...")
    
    try:
        from src.config import Config
        print("✅ Config module")
    except ImportError as e:
        print(f"❌ Config module: {e}")
        return False
    
    try:
        from src.logger import setup_logger
        print("✅ Logger module")
    except ImportError as e:
        print(f"❌ Logger module: {e}")
        return False
    
    try:
        from src.pexels_api import PexelsAPI
        print("✅ PexelsAPI module")
    except ImportError as e:
        print(f"❌ PexelsAPI module: {e}")
        return False
    
    try:
        from src.video_processor import VideoProcessor
        print("✅ VideoProcessor module")
    except ImportError as e:
        print(f"❌ VideoProcessor module: {e}")
        return False
    
    try:
        from src.gui import BackgroundVideoGUI
        print("✅ GUI module")
    except ImportError as e:
        print(f"❌ GUI module: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist."""
    print("\n🔍 Testing directories...")
    
    if Path("logs").exists():
        print("✅ logs directory")
    else:
        print("❌ logs directory")
        return False
    
    if Path("src").exists():
        print("✅ src directory")
    else:
        print("❌ src directory")
        return False
    
    return True

def test_config():
    """Test configuration functionality."""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.config import Config
        config = Config()
        print("✅ Configuration loaded")
        
        # Test setting and getting values
        config.set("test_key", "test_value")
        if config.get("test_key") == "test_value":
            print("✅ Configuration read/write")
        else:
            print("❌ Configuration read/write")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Background Video Generator - Installation Test")
    print("=" * 55)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test FFmpeg
    if not test_ffmpeg():
        all_tests_passed = False
    
    # Test application modules
    if not test_application_modules():
        all_tests_passed = False
    
    # Test directories
    if not test_directories():
        all_tests_passed = False
    
    # Test configuration
    if not test_config():
        all_tests_passed = False
    
    print("\n" + "=" * 55)
    if all_tests_passed:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo start the application:")
        print("   python main.py")
    else:
        print("❌ Some tests failed. Please check the installation.")
        print("\nCommon solutions:")
        print("   1. Run 'python install.py' to install dependencies")
        print("   2. Install FFmpeg if not already installed")
        print("   3. Make sure you're in the correct directory")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
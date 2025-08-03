#!/usr/bin/env python3
"""
py2exe Setup Script for BackgroundPython
Creates a standalone executable from the Python application.
"""

import sys
import os
from cx_Freeze import setup, Executable

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Define the base for the executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use Win32GUI for Windows applications

# Define the executable
executables = [
    Executable(
        script="../main.py",  # Path to the main script
        base=base,
        target_name="BackgroundPython.exe",  # Name of the output executable
        icon=None,  # You can add an icon file here if you have one
        shortcut_name="BackgroundPython",
        shortcut_dir="DesktopFolder"
    )
]

# Define packages to include
packages = [
    "src",
    "requests",
    "cv2",
    "moviepy",
    "PIL",
    "dotenv",
    "tqdm",
    "loguru",
    "subprocess",
    "os",
    "sys",
    "time",
    "json",
    "logging"
]

# Define files to include
include_files = [
    ("../requirements.txt", "requirements.txt"),
    ("../README.md", "README.md"),
    ("../config.json", "config.json"),
    ("../run.bat", "run.bat"),
    ("../run.sh", "run.sh"),
    ("../.gitignore", ".gitignore"),
]

# Define excluded modules (to reduce size)
excludes = [
    "tkinter",
    "unittest",
    "email",
    "http",
    "urllib",
    "xml",
    "pydoc",
    "doctest",
    "argparse",
    "difflib",
    "inspect",
    "pdb",
    "profile",
    "pstats",
    "traceback",
    "calendar",
    "pipes",
    "nntplib",
    "smtplib",
    "socketserver",
    "xmlrpc",
    "lib2to3",
    "pydoc_data",
    "test",
    "distutils",
    "setuptools",
    "pip",
    "wheel",
    "pkg_resources",
]

# Setup configuration
setup(
    name="BackgroundPython",
    version="1.0.0",
    description="Background Video Generator - A Python application for creating background videos from Pexels clips",
    author="Dean Kruger",
    options={
        "build_exe": {
            "packages": packages,
            "include_files": include_files,
            "excludes": excludes,
            "include_msvcr": True,  # Include Microsoft Visual C++ Runtime
            "optimize": 2,  # Optimize bytecode
            "compressed": True,  # Compress the executable
        }
    },
    executables=executables
) 
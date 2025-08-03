# BackgroundPython Executable Builder

This folder contains scripts and configuration files to create a standalone executable from the BackgroundPython application using cx_Freeze.

## Prerequisites

- Python 3.8 or higher
- All dependencies from the main `requirements.txt` file
- cx_Freeze (will be installed automatically by the build scripts)

## Quick Start

### Option 1: Using Batch Script (Windows)
```cmd
cd py2exe
build.bat
```

### Option 2: Using PowerShell Script (Windows)
```powershell
cd py2exe
.\build.ps1
```

### Option 3: Manual Build
```cmd
cd py2exe
pip install cx_Freeze
python setup.py build
```

## Build Scripts

### build.bat
- Simple batch script for Windows
- Automatically installs cx_Freeze if not present
- Cleans previous builds
- Provides basic error handling

### build.ps1
- PowerShell script with enhanced features
- Better error handling and colored output
- Supports parameters:
  - `-Clean`: Clean previous build artifacts
  - `-InstallDeps`: Install build dependencies
- Shows file size and location of created executable

## Configuration

### setup.py
The main configuration file that defines:
- **Executable settings**: Name, icon, base type
- **Packages to include**: All required Python modules
- **Files to include**: Configuration files, documentation
- **Excluded modules**: Unused modules to reduce size
- **Build options**: Optimization, compression, MSVC runtime

### Key Configuration Options

```python
# Executable settings
target_name="BackgroundPython.exe"  # Output executable name
base="Win32GUI"  # Use GUI mode (no console window)

# Included packages
packages = ["src", "requests", "cv2", "moviepy", "PIL", ...]

# Included files
include_files = [
    ("../requirements.txt", "requirements.txt"),
    ("../README.md", "README.md"),
    ("../config.json", "config.json"),
    # ... other files
]

# Build optimizations
"optimize": 2,  # Optimize bytecode
"compressed": True,  # Compress the executable
"include_msvcr": True,  # Include MSVC runtime
```

## Output

After successful build, the executable will be located at:
```
dist/exe.win-amd64-3.x/BackgroundPython.exe
```

The `dist` folder contains:
- `BackgroundPython.exe` - The main executable
- All required DLLs and dependencies
- Included files (config.json, README.md, etc.)

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Ensure Python is installed and in PATH
   - Try running `python --version` to verify

2. **"cx_Freeze not found"**
   - Run `pip install cx_Freeze` manually
   - Or use `.\build.ps1 -InstallDeps`

3. **Build fails with import errors**
   - Check that all dependencies are installed
   - Verify the `packages` list in setup.py includes all required modules

4. **Executable is too large**
   - Review the `excludes` list in setup.py
   - Remove unused packages from the `packages` list

5. **Executable doesn't run**
   - Check if all required files are included in `include_files`
   - Verify the application works when run as Python script first

### Debug Mode

To build with debug information:
```python
# In setup.py, change:
"optimize": 0,  # No optimization
```

### Alternative Build Tools

If cx_Freeze doesn't work for your needs, consider:

1. **PyInstaller**
   ```cmd
   pip install pyinstaller
   pyinstaller --onefile --windowed main.py
   ```

2. **auto-py-to-exe** (GUI tool)
   ```cmd
   pip install auto-py-to-exe
   auto-py-to-exe
   ```

## Distribution

The created executable is self-contained and can be distributed by:
1. Copying the entire `dist/exe.win-amd64-3.x/` folder
2. Creating an installer using tools like Inno Setup or NSIS
3. Zipping the folder for easy distribution

## Notes

- The executable size will be larger than the Python script due to included dependencies
- First run may be slower as the executable extracts temporary files
- Test the executable on a clean system to ensure all dependencies are included
- Consider creating an installer for professional distribution 
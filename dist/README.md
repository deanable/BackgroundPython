# BackgroundPython Single Executable Builder

This folder contains scripts and configuration files to create a **single standalone executable** from the BackgroundPython application using PyInstaller.

## 🎯 **Key Benefits**

- **Single File**: Creates one `.exe` file instead of multiple files
- **Self-Contained**: No external dependencies required
- **Easy Distribution**: Just copy one file to any Windows machine
- **Optimized**: Compressed and optimized for size and performance

## Prerequisites

- Python 3.8 or higher
- All dependencies from the main `requirements.txt` file
- PyInstaller (will be installed automatically by the build scripts)

## Quick Start

### Option 1: Using Batch Script (Windows)
```cmd
cd dist
build.bat
```

### Option 2: Using PowerShell Script (Windows)
```powershell
cd dist
.\build.ps1
```

### Option 3: Manual Build
```cmd
cd dist
pip install pyinstaller
pyinstaller BackgroundPython.spec
```

## Build Scripts

### build.bat
- Simple batch script for Windows
- Automatically installs PyInstaller if not present
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

### BackgroundPython.spec
The main configuration file that defines:
- **Single file mode**: Creates one executable instead of multiple files
- **Hidden imports**: All required Python modules
- **Data files**: Configuration files, documentation
- **Excluded modules**: Unused modules to reduce size
- **Build optimizations**: UPX compression, no console window

### Key Configuration Options

```python
# Single file settings
console=False,  # No console window (GUI mode)
upx=True,  # Enable UPX compression
runtime_tmpdir=None,  # Extract to temp directory

# Included data files
datas=[
    ('../config.json', '.'),
    ('../README.md', '.'),
    ('../requirements.txt', '.'),
]

# Hidden imports (required modules)
hiddenimports=[
    'src', 'requests', 'cv2', 'moviepy', 'PIL', ...
]
```

## Output

After successful build, you'll get:
```
dist/BackgroundPython.exe  # Single standalone executable
```

**That's it!** Just one file that contains everything needed to run the application.

## Advantages Over Other Tools

### vs cx_Freeze (py2exe)
- ✅ **Single file** vs multiple files
- ✅ **Easier distribution** - just one file to copy
- ✅ **Better compression** with UPX
- ✅ **More reliable** on different systems

### vs auto-py-to-exe
- ✅ **Command line** automation
- ✅ **Version control** friendly
- ✅ **CI/CD** integration ready
- ✅ **Consistent builds**

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Ensure Python is installed and in PATH
   - Try running `python --version` to verify

2. **"PyInstaller not found"**
   - Run `pip install pyinstaller` manually
   - Or use `.\build.ps1 -InstallDeps`

3. **Build fails with import errors**
   - Check that all dependencies are installed
   - Verify the `hiddenimports` list in the spec file

4. **Executable is too large**
   - Review the `excludes` list in the spec file
   - Remove unused packages from `hiddenimports`

5. **Executable doesn't run**
   - Check if all required files are included in `datas`
   - Verify the application works when run as Python script first

### Debug Mode

To build with debug information:
```python
# In BackgroundPython.spec, change:
debug=True,  # Enable debug mode
console=True,  # Show console window
```

### Alternative Build Commands

If you prefer direct PyInstaller commands:

```bash
# Basic single file build
pyinstaller --onefile --windowed ../main.py

# With custom name
pyinstaller --onefile --windowed --name BackgroundPython ../main.py

# With icon
pyinstaller --onefile --windowed --icon=icon.ico ../main.py
```

## Distribution

The created executable is completely self-contained and can be distributed by:
1. **Copying the single `.exe` file** to any Windows machine
2. **Creating an installer** using tools like Inno Setup or NSIS
3. **Uploading to cloud storage** for easy download

## Performance Notes

- **First run**: May be slower as the executable extracts temporary files
- **Subsequent runs**: Faster as files are cached
- **File size**: Typically 50-200MB depending on dependencies
- **Memory usage**: Similar to running the Python script directly

## Security Considerations

- The executable contains all source code (though compiled)
- Consider code signing for professional distribution
- Test thoroughly on clean systems before distribution

## Notes

- The executable size will be larger than the Python script due to included dependencies
- First run may be slower as the executable extracts temporary files
- Test the executable on a clean system to ensure all dependencies are included
- The single file approach is perfect for distribution and deployment 
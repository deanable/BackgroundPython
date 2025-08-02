# Background Video Generator (Python)

A Python application that creates background videos by downloading and concatenating clips from Pexels.

## Features

* Search and download video clips from Pexels API
* Automatic video normalization and concatenation
* Support for 1080p and 4K resolutions
* Horizontal and vertical aspect ratios
* Configurable video duration
* Advanced logging system for debugging
* Cross-platform compatibility (Windows, macOS, Linux)

## Advanced Logging System

The application includes a comprehensive logging system that creates detailed logs for debugging the video creation pipeline.

### Log File Location

Log files are stored in the `logs` folder within the application directory:

```
BackgroundPython/logs/
```

### Log File Naming

Each application run creates a new log file with a timestamp:

```
log-YYYY-MM-DD_HH-mm-ss.log
```

Example: `log-2024-01-15_14-30-25.log`

### Log Levels

The logging system supports multiple log levels:

* **DEBUG**: Detailed debugging information
* **INFO**: General information about operations
* **WARNING**: Warning messages for non-critical issues
* **ERROR**: Error messages and exceptions

### Log Categories

The logging system tracks different aspects of the video creation pipeline:

#### Pipeline Steps

* Application initialization
* API search operations
* Download and normalization phases
* Video concatenation
* Cleanup operations

#### Performance Metrics

* API call response times
* Download speeds for individual clips
* Normalization processing times
* Overall pipeline completion time
* Memory usage tracking

#### File Operations

* File downloads with sizes
* File deletions during cleanup
* Final video creation with file size

#### API Calls

* Pexels API requests and responses
* Success/failure status
* Search parameters

#### Video Processing

* All video processing operations
* Input and output file information
* Processing parameters

#### System Information

* Operating system details
* Python version
* Available memory
* Application version

## Requirements

* Python 3.8 or later
* FFmpeg installed and accessible in PATH
* Pexels API key

## Installation

### Quick Start

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/deanable/BackgroundPython.git
   cd BackgroundPython
   ```

2. **Run the installation script**
   ```bash
   python install.py
   ```

3. **Get a Pexels API key**
   - Visit [Pexels API](https://www.pexels.com/api/)
   - Sign up for a free account
   - Generate an API key

4. **Install FFmpeg** (if not already installed)
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html) or use [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
   - **macOS**: Use [Homebrew](https://brew.sh/): `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

5. **Run the application**
   ```bash
   python main.py
   ```
   
   **Alternative ways to run:**
   - **Windows**: Double-click `run.bat` or run `run.bat` in Command Prompt
   - **macOS/Linux**: Run `./run.sh` in Terminal (make executable first: `chmod +x run.sh`)

6. **Test the installation** (optional)
   ```bash
   python test_installation.py
   ```

### Manual Installation

If you prefer to install manually:

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create logs directory**
   ```bash
   mkdir logs
   ```

3. **Follow steps 3-5 from Quick Start above**

## Usage

1. Enter your Pexels API key
2. Enter a search term for video clips
3. Adjust duration, resolution, and aspect ratio settings
4. Click "Start" to begin video generation
5. Monitor progress in the status bar
6. Check logs in the `logs` folder for detailed information

## Configuration

Settings are automatically saved to a JSON configuration file and restored on application startup:

* API key
* Search term
* Duration setting
* Resolution preference
* Aspect ratio preference
* Window position and size

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is installed and in PATH
2. **API key issues**: Verify your Pexels API key is valid
3. **No videos found**: Try different search terms
4. **Slow performance**: Check log files for performance bottlenecks

### Using Logs for Debugging

1. Run the application and reproduce the issue
2. Check the latest log file in the `logs` folder
3. Look for ERROR entries to identify the problem
4. Review the pipeline steps to understand where the issue occurred
5. Check system information for resource constraints

## License

This project is licensed under the MIT License.

## About

Python version of the BackgroundVideoGenerator, designed to handle video processing more efficiently than the C# version. 
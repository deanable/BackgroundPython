#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for BackgroundPython single executable using PyInstaller

.DESCRIPTION
    This script creates a single standalone executable from the BackgroundPython application.

.PARAMETER Clean
    Clean previous build artifacts before building

.PARAMETER InstallDeps
    Install required dependencies before building

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
    .\build.ps1 -InstallDeps
#>

param(
    [switch]$Clean,
    [switch]$InstallDeps
)

Write-Host "Building BackgroundPython Single Executable..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Error "Python is not installed or not in PATH"
    exit 1
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    try {
        pip install pyinstaller
        Write-Host "PyInstaller installed successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to install PyInstaller"
        exit 1
    }
}

# Check if PyInstaller is available
try {
    python -c "import PyInstaller" 2>&1 | Out-Null
    Write-Host "PyInstaller is available" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    try {
        pip install pyinstaller
    } catch {
        Write-Error "Failed to install PyInstaller. Please run with -InstallDeps flag."
        exit 1
    }
}

# Clean previous build if requested or if build directories exist
if ($Clean -or (Test-Path "build") -or (Test-Path "BackgroundPython.exe")) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
    if (Test-Path "BackgroundPython.exe") {
        Remove-Item -Force "BackgroundPython.exe"
    }
    Write-Host "Clean completed" -ForegroundColor Green
}

# Build the executable
Write-Host "Building single executable..." -ForegroundColor Yellow
try {
    python -m PyInstaller BackgroundPython.spec
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Build completed successfully!" -ForegroundColor Green
        Write-Host "Executable location: BackgroundPython.exe" -ForegroundColor Cyan
        Write-Host ""
        
        # Check if executable was created
        if (Test-Path "dist\BackgroundPython.exe") {
            $fileSize = [math]::Round((Get-Item "dist\BackgroundPython.exe").Length / 1MB, 2)
            Write-Host "Executable created successfully!" -ForegroundColor Green
            Write-Host "File size: $fileSize MB" -ForegroundColor Cyan
            Write-Host "Location: $(Get-Item 'dist\BackgroundPython.exe').FullName" -ForegroundColor Green
            
            # Clean up build artifacts
            Write-Host ""
            Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
            if (Test-Path "build") {
                Remove-Item -Recurse -Force "build"
                Write-Host "Removed build directory" -ForegroundColor Green
            }
            if (Test-Path "__pycache__") {
                Remove-Item -Recurse -Force "__pycache__"
                Write-Host "Removed __pycache__ directory" -ForegroundColor Green
            }
            if (Test-Path "*.spec") {
                Get-ChildItem "*.spec" | Where-Object { $_.Name -ne "BackgroundPython.spec" } | Remove-Item -Force
                Write-Host "Removed temporary spec files" -ForegroundColor Green
            }
            Write-Host "Cleanup completed!" -ForegroundColor Green
        } else {
            Write-Warning "Executable not found in expected location"
        }
    } else {
        Write-Error "Build failed with exit code: $LASTEXITCODE"
        exit 1
    }
} catch {
    Write-Error "Build failed: $_"
    exit 1
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
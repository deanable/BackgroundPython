#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for BackgroundPython executable using cx_Freeze

.DESCRIPTION
    This script automates the process of creating a standalone executable
    from the BackgroundPython application using cx_Freeze.

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

Write-Host "Building BackgroundPython Executable..." -ForegroundColor Green
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
    Write-Host "Installing cx_Freeze..." -ForegroundColor Yellow
    try {
        pip install cx_Freeze
        Write-Host "cx_Freeze installed successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to install cx_Freeze"
        exit 1
    }
}

# Check if cx_Freeze is available
try {
    python -c "import cx_Freeze" 2>&1 | Out-Null
    Write-Host "cx_Freeze is available" -ForegroundColor Green
} catch {
    Write-Host "cx_Freeze not found. Installing..." -ForegroundColor Yellow
    try {
        pip install cx_Freeze
    } catch {
        Write-Error "Failed to install cx_Freeze. Please run with -InstallDeps flag."
        exit 1
    }
}

# Clean previous build if requested or if build directories exist
if ($Clean -or (Test-Path "build") -or (Test-Path "dist")) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
    }
    Write-Host "Clean completed" -ForegroundColor Green
}

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
try {
    python setup.py build
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Build completed successfully!" -ForegroundColor Green
        Write-Host "Executable location: dist\exe.win-amd64-3.x\BackgroundPython.exe" -ForegroundColor Cyan
        Write-Host ""
        
        # Check if executable was created
        $exePath = Get-ChildItem -Path "dist" -Recurse -Name "BackgroundPython.exe" -ErrorAction SilentlyContinue
        if ($exePath) {
            $fullPath = (Get-Item "dist").FullName + "\" + $exePath[0]
            Write-Host "Executable found at: $fullPath" -ForegroundColor Green
            $fileSize = [math]::Round((Get-Item $fullPath).Length / 1MB, 2)
            Write-Host "File size: $fileSize MB" -ForegroundColor Cyan
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
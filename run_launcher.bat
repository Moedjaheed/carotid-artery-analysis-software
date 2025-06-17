@echo off
title Carotid Segmentation Launcher - Enhanced Analytics Suite
echo ========================================
echo    Carotid Artery Segmentation Suite
echo    Enhanced with Advanced Analytics and Pressure Integration
echo ========================================
echo.
echo Available Features:
echo [Core Functions]
echo - Training Model
echo - Video Inference (Auto)
echo - Enhanced Inference (with Pressure Integration) NEW!
echo - Select Subject for Inference
echo - Enhanced Data Viewer (Overlay + Diameter/Pressure Analysis) NEW!
echo - View Inference Results
echo.
echo [Quick Access]
echo - Press 'D' for Direct Enhanced Data Viewer Launch
echo - Press 'F' for Frame Comparison Viewer (NEW!)
echo - Press 'G' for Full GUI Launcher
echo.
echo [NEW: Advanced Features]
echo - Enhanced Inference with Multiple Subject Selection (Checkboxes)
echo - Model Selection with Radiobuttons (UNet variants)
echo - Enhanced Inference with Pressure Data Integration
echo - Enhanced Data Viewer (Overlay Video + Real-time Analysis)
echo - Frame Comparison Viewer (Dual Frame Analysis with Vertical Lines) NEW!
echo - Advanced Analytics Dashboard
echo - Batch Process All Subjects with Progress Monitoring
echo - Comprehensive Statistical Analysis
echo - Clinical Recommendations System
echo - Multi-format Export (JSON/CSV/Excel)
echo.
echo [Utilities]
echo - Dependencies Management
echo - Project Folder Access
echo.
echo Latest Updates:
echo - NEW: Frame Comparison Viewer with dual vertical line indicators
echo - NEW: Interactive plot selection for frame comparison
echo - NEW: Multiple Subject Selection with Checkboxes for batch processing
echo - NEW: Model Selection with Radiobuttons (choose between different UNet models)
echo - Enhanced Inference with pressure integration and progress monitoring
echo - Enhanced Data Viewer with overlay and real-time analysis
echo - Subject dropdown selection with status preview
echo - Smart data synchronization and dual-axis plotting
echo - Real-time subject selection with pressure status
echo - Advanced correlation analysis (diameter vs pressure)
echo - Segmented video overlay display with original size preservation
echo - Fixed OpenMP conflicts for stable processing
echo - Comprehensive configuration save/load functionality
echo - Comprehensive documentation and troubleshooting
echo ========================================
echo.
echo Quick Launch Options:
echo [D] Launch Enhanced Data Viewer directly
echo [F] Launch Frame Comparison Viewer (NEW!)
echo [G] Launch Full GUI Launcher
echo [Enter] Continue with standard launcher
echo.
set /p choice="Your choice (D/F/G/Enter): "
echo.

:: Handle quick launch choices
if /I "%choice%"=="D" (
    echo ========================================
    echo    Launching Enhanced Data Viewer
    echo    Direct Access - Overlay and Analysis
    echo ========================================
    echo.
    goto launch_data_viewer
)

if /I "%choice%"=="F" (
    echo ========================================
    echo    Launching Frame Comparison Viewer
    echo    Dual Frame Analysis with Vertical Lines
    echo ========================================
    echo.
    goto launch_frame_comparison
)

if /I "%choice%"=="G" (
    echo ========================================
    echo    Launching Full GUI Launcher
    echo    All Features Available
    echo ========================================
    echo.
    goto launch_gui
)

echo ========================================
echo    Launching Standard Mode
echo ========================================
echo.

:launch_gui

:: Check if conda environment exists
conda info --envs | findstr "ridho-ta" > nul
if %errorlevel% neq 0 (
    echo Warning: ridho-ta conda environment not found
    echo You may need to create it first: conda create -n ridho-ta python=3.8
    echo.
)

:: Try to activate conda environment
echo Activating conda environment: ridho-ta
call conda activate ridho-ta 2>nul
if %errorlevel% neq 0 (
    echo Warning: Could not activate ridho-ta environment
    echo Running with current Python environment
    echo.
)

:: Check which launcher to use (prioritize enhanced fixed version)
if exist "launcher_enhanced_fixed.py" (
    echo Using ENHANCED FIXED launcher with Multiple Subject Selection and Model Choice...
    echo Loading: launcher_enhanced_fixed.py
    echo.
    echo Enhanced Features Available:
    echo - Multiple Subject Selection with Checkboxes
    echo - Model Selection with Radiobuttons    echo - Enhanced Inference with Pressure Data Integration
    echo - Enhanced Data Viewer with overlay video display
    echo - Subject selection with pressure availability status
    echo - Real-time processing logs with progress monitoring
    echo - Advanced correlation analysis (diameter vs pressure)
    echo - Diameter/Pressure plot with frame-based X-axis
    echo - Batch processing for all subjects
    echo - Comprehensive analytics dashboard
    echo - Configuration save/load functionality
    echo.
    python launcher_enhanced_fixed.py
) else if exist "launcher_with_inference_log.py" (
    echo Using FALLBACK launcher (may have syntax issues)...
    echo Loading: launcher_with_inference_log.py
    echo.    echo Enhanced Features Available:
    echo - Enhanced Inference with Pressure Data Integration
    echo - Enhanced Data Viewer with overlay video display
    echo - Subject selection with pressure availability status
    echo - Real-time processing logs with progress monitoring
    echo - Advanced correlation analysis (diameter vs pressure)
    echo - Diameter/Pressure plot with frame-based X-axis
    echo - Batch processing for all subjects
    echo - Comprehensive analytics dashboard
    echo.
    python launcher_with_inference_log.py
) else if exist "launcher_new.py" (
    echo Using new launcher...
    echo Loading: launcher_new.py
    echo.
    python launcher_new.py
) else if exist "launcher.py" (
    echo Using default launcher...
    echo Loading: launcher.py
    echo.
    python launcher.py
) else (    echo ERROR: No launcher file found!
    echo Please ensure launcher_with_inference_log.py exists (RECOMMENDED)
    echo.    echo The enhanced launcher includes:
    echo - Enhanced Inference with Pressure Integration
    echo - Enhanced Data Viewer with overlay and real-time analysis
    echo - Advanced Analytics Dashboard
    echo - Batch Processing System
    echo - Real-time monitoring and logging
    echo - Comprehensive correlation analysis
    echo.
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Launcher failed to start
    echo Error code: %errorlevel%
    echo.    echo Troubleshooting:
    echo - Check if Python is installed and in PATH
    echo - Ensure all dependencies are installed
    echo - Try running: pip install -r requirements.txt
    echo - Check if model file UNet_25Mei_Sore.pth exists
    echo.    echo For Enhanced Inference with Pressure Integration:
    echo - Ensure pressure files (subjectN.csv) exist in data_uji/SubjekN/
    echo - Ensure timestamp files (timestamps.csv) exist in data_uji/SubjekN/
    echo - Check DOKUMENTASI_ENHANCED_INFERENCE.md for details
    echo.
    echo For Advanced Analytics features:
    echo - Ensure seaborn and openpyxl are installed
    echo - Check that inference results exist in inference_results/ folder
    echo - Verify data_uji/ folder contains subject data
    echo.
)

goto end_launcher

:launch_frame_comparison

:: Check if conda environment exists
conda info --envs | findstr "ridho-ta" > nul
if %errorlevel% neq 0 (
    echo Warning: ridho-ta conda environment not found
    echo You may need to create it first: conda create -n ridho-ta python=3.8
    echo.
)

:: Try to activate conda environment
echo Activating conda environment: ridho-ta
call conda activate ridho-ta 2>nul
if %errorlevel% neq 0 (
    echo Warning: Could not activate ridho-ta environment
    echo Running with current Python environment
    echo.
)

:: Launch Frame Comparison Viewer directly
if exist "frame_comparison_viewer.py" (
    echo Launching Frame Comparison Viewer...
    echo.
    echo Features:
    echo - Dual frame display with comparison
    echo - Interactive vertical line indicators (Blue for Frame 1, Red for Frame 2)
    echo - Real-time diameter vs pressure analysis
    echo - Click on plot to set frame positions
    echo - Synchronized data visualization
    echo - Theme support (Light/Dark modes)
    echo.
    python frame_comparison_viewer.py
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Frame Comparison Viewer failed to start
        echo Error code: %errorlevel%
        echo.
        echo Troubleshooting:
        echo - Check if all dependencies are installed: pip install -r requirements.txt
        echo - Ensure tkinter is available (should be included with Python)
        echo - Check if data_uji/ folder exists with subject data
        echo - Verify inference_results/ folder exists for analysis data
        echo - Ensure matplotlib and PIL are properly installed
        echo.
        pause
        exit /b 1
    )
) else (
    echo ERROR: frame_comparison_viewer.py not found!
    echo Please ensure the Frame Comparison Viewer file exists
    echo.
    pause
    exit /b 1
)

goto end_launcher

:launch_data_viewer

:: Check if conda environment exists
conda info --envs | findstr "ridho-ta" > nul
if %errorlevel% neq 0 (
    echo Warning: ridho-ta conda environment not found
    echo You may need to create it first: conda create -n ridho-ta python=3.8
    echo.
)

:: Try to activate conda environment
echo Activating conda environment: ridho-ta
call conda activate ridho-ta 2>nul
if %errorlevel% neq 0 (
    echo Warning: Could not activate ridho-ta environment
    echo Running with current Python environment
    echo.
)

:: Launch Enhanced Data Viewer directly
if exist "data_viewer.py" (
    echo Launching Enhanced Data Viewer...
    echo.
    echo Features:
    echo - Subject dropdown with status preview
    echo - Segmented video overlay display
    echo - Real-time diameter vs pressure analysis
    echo - Frame-based X-axis plotting
    echo - Automatic data synchronization
    echo.
    python data_viewer.py
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Enhanced Data Viewer failed to start
        echo Error code: %errorlevel%
        echo.
        echo Troubleshooting:
        echo - Check if all dependencies are installed: pip install -r requirements.txt
        echo - Ensure tkinter is available (should be included with Python)
        echo - Check if data_uji/ folder exists with subject data
        echo - Verify inference_results/ folder exists for analysis data
        echo.
        pause
        exit /b 1
    )
) else (
    echo ERROR: data_viewer.py not found!
    echo Please ensure the Enhanced Data Viewer file exists
    echo.
    pause
    exit /b 1
)

goto end_launcher

:end_launcher

echo.
echo ========================================
echo Thank you for using Carotid Segmentation Suite!
echo Enhanced Analytics Suite with Pressure Integration & Data Viewer - Version 3.2
echo.
echo Key Features:
echo - Enhanced Data Viewer with segmented video overlay
echo - Frame Comparison Viewer with dual vertical line indicators (NEW!)
echo - Real-time diameter vs pressure analysis
echo - Frame-based correlation plots
echo - Interactive plot selection for frame comparison
echo - Original size image preservation
echo - Theme support (Light/Dark modes)
echo.
echo For questions or support, check:
echo - COMPLETION_SUMMARY.md (Latest Implementation Status)
echo - DOKUMENTASI_ENHANCED_INFERENCE.md (Pressure Integration Guide)
echo - STATUS_ENHANCED_INFERENCE.md (Implementation Status)
echo - DOKUMENTASI_ADVANCED_ANALYTICS.md (Analytics Features)
echo - README.md (General Documentation)
echo ========================================
pause

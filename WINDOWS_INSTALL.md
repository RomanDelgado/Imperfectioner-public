# Windows Installation Guide

## Prerequisites
1. Python 3.11 or higher
2. Microsoft Visual C++ Build Tools
   - **Important**: This is required for building the `python-rtmidi` package
   - Without this, you will get the error: "Microsoft Visual C++ 14.0 or greater is required"

## Step 1: Install Visual C++ Build Tools
1. Download Visual Studio Build Tools:
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Click "Download Build Tools"

2. Run the installer:
   - When the Visual Studio Installer opens, select:
     - "Desktop development with C++"
   - This will install the necessary components for building Python packages

3. After installation:
   - Restart your computer (or at minimum, restart your terminal)

## Step 2: Python Environment Setup
1. Open a new terminal (Command Prompt or PowerShell)
2. Navigate to your project directory
3. Create a virtual environment:
   ```bat
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```bat
   .\venv\Scripts\activate
   ```

## Step 3: Install Dependencies
Install packages in this specific order:
```bat
pip install numpy==2.2.0
pip install sounddevice==0.5.1
pip install python-rtmidi==1.5.8
```

## Troubleshooting

### If you see "Microsoft Visual C++ 14.0 or greater is required":
- Make sure you've installed the Visual C++ Build Tools as described in Step 1
- Make sure you've selected "Desktop development with C++" during installation
- Try restarting your terminal and computer

### If rtmidi fails to detect MIDI devices:
- Ensure your MIDI device is connected before starting the application
- The application will fall back to a mock MIDI interface for testing if no hardware is detected

### If you have no audio output:
- The synthesizer will use a null audio backend for testing if no audio device is available
- You should still see MIDI event information in the console

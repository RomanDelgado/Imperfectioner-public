# Windows Installation Guide for VS Code

## Prerequisites
1. Python 3.11 or higher
2. Visual Studio Code with Python extension
3. Microsoft Visual C++ Build Tools
   - **Important**: This is just the build tools, not Visual Studio IDE
   - This is required for building the `python-rtmidi` package
   - Without this, you will get the error: "Microsoft Visual C++ 14.0 or greater is required"

## Step 1: VS Code Setup
1. Download and install Visual Studio Code:
   - Go to: https://code.visualstudio.com/
   - Download and run the installer

2. Install the Python extension in VS Code:
   - Open VS Code
   - Click the Extensions icon (Ctrl+Shift+X)
   - Search for "Python"
   - Install the Microsoft Python extension

## Step 2: Install Visual C++ Build Tools
1. Download Visual Studio Build Tools:
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Click "Download Build Tools"
   - **Important**: This is NOT Visual Studio IDE, just the build tools

2. Run the installer:
   - When the Visual Studio Installer opens, select:
     - "Desktop development with C++"
   - This will install the necessary components for building Python packages

3. After installation:
   - Restart your computer to ensure all components are properly registered
   - Open VS Code again

## Step 3: Python Environment Setup
1. Install Python 3.11 if not already installed:
   - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. Open VS Code:
   - Open the project folder: File > Open Folder
   - Open VS Code's integrated terminal: View > Terminal
   - Make sure you're in the project directory

3. Create a virtual environment:
   ```bat
   python -m venv venv
   ```

4. Select the Python interpreter:
   - Press Ctrl+Shift+P to open Command Palette
   - Type "Python: Select Interpreter"
   - Choose the interpreter from the venv folder
     (Usually ends with 'venv/Scripts/python.exe')

5. Open a new terminal in VS Code:
   - This will automatically activate the virtual environment
   - You should see (venv) at the start of the terminal prompt
   - If not, run: `.\venv\Scripts\activate`

## Step 4: Install Dependencies
Install packages in this specific order:
```bat
# 1. Install numpy first
pip install numpy==2.2.0

# 2. Install sounddevice
pip install sounddevice==0.5.1

# 3. Finally install python-rtmidi
pip install python-rtmidi==1.5.8
```

## Troubleshooting

### If python-rtmidi fails to install:
1. Verify Visual C++ Build Tools:
   - Open "Visual Studio Installer"
   - Click "Modify" on Build Tools
   - Ensure "Desktop development with C++" is checked
   - Look for "MSVC build tools" and "Windows SDK" components

2. If still failing:
   - Open a new Command Prompt as Administrator
   - Navigate to your project directory
   - Run the pip install commands again

### If MIDI devices aren't detected:
- Check Device Manager for your MIDI device
- The synthesizer will automatically use a mock MIDI interface for testing
- You'll still see all MIDI debug information in the console

### If you have no audio output:
- Check Windows Sound settings for your output device
- The synthesizer will use a null audio backend if no device is found
- You'll still see all synthesizer activity in the console

### VS Code-specific issues:
1. If Python isn't recognized:
   - Close VS Code completely
   - Open Task Manager and end any VS Code processes
   - Restart VS Code
   - Or run: Ctrl+Shift+P > "Developer: Reload Window"

2. Virtual environment issues:
   - Delete the venv folder
   - Create it again: `python -m venv venv`
   - Select interpreter again: Ctrl+Shift+P > "Python: Select Interpreter"

3. Terminal shows wrong Python version:
   - Open a new terminal: Terminal > New Terminal
   - Or run: Ctrl+Shift+` (backtick)

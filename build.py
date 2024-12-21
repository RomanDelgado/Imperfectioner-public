
"""
Local Development Setup Guide
===========================

Prerequisites:
-------------
1. Python 3.11 or higher
2. Visual Studio Code with Python extension
3. Microsoft Visual C++ Build Tools (Windows only)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Note: This is just the build tools, not Visual Studio IDE
   - During installation, select "Desktop development with C++" workload
   - Required for python-rtmidi package compilation
4. VS Code Python extension settings:
   - Select Python interpreter from your virtual environment
   - Terminal: Activate virtual environment automatically

VS Code Setup:
------------
1. Open VS Code
2. Install Python extension if not already installed:
   - Click Extensions icon (or Ctrl+Shift+X)
   - Search for "Python"
   - Install Microsoft's Python extension

3. Configure VS Code:
   - Open Command Palette (Ctrl+Shift+P)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment
   - VS Code will automatically activate the environment in new terminals

Troubleshooting:
--------------
If you see "Microsoft Visual C++ 14.0 or greater is required":
1. Install Visual C++ Build Tools from the link above
2. Make sure to select "Desktop development with C++"
3. Restart VS Code completely
4. Open a new terminal and try installing again

Note: Dependencies are managed through pyproject.toml
"""

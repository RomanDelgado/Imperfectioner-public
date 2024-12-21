
"""
Local Development Setup Guide
===========================

Prerequisites:
-------------
1. Python 3.11 or higher
2. Microsoft Visual C++ Build Tools (Windows only)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++" workload during installation
   - Required for python-rtmidi package compilation

Installation Steps:
-----------------
1. Create a virtual environment:
   python -m venv venv

2. Activate the virtual environment:
   - Windows: .\venv\Scripts\activate
   - Unix: source venv/bin/activate

3. Install dependencies in order:
   pip install numpy==2.2.0
   pip install sounddevice==0.5.1
   pip install python-rtmidi==1.5.8

Troubleshooting:
--------------
If you see "Microsoft Visual C++ 14.0 or greater is required":
1. Install Visual C++ Build Tools from the link above
2. Make sure to select "Desktop development with C++"
3. Restart your terminal and try installing again

Note: Dependencies are managed through pyproject.toml
"""

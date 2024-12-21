
import subprocess
import sys
import os

def install_package(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False

def main():
    print("MIDI Synthesizer - Windows Dependency Installer")
    print("=============================================")
    
    # Required packages
    packages = [
        "numpy==2.2.0",
        "python-rtmidi==1.5.8",
        "sounddevice==0.5.1"
    ]
    
    # Install each package
    success = True
    for package in packages:
        if not install_package(package):
            success = False
            
    if success:
        print("\nAll dependencies installed successfully!")
        print("You can now run the synthesizer with: python synth.py")
    else:
        print("\nSome dependencies failed to install.")
        print("Please make sure you have Microsoft Visual C++ Build Tools installed.")
        print("Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/")

if __name__ == "__main__":
    main()

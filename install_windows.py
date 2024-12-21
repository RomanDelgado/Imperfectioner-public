
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
        "sounddevice==0.5.1",
        "mido==1.3.2"
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

if __name__ == "__main__":
    main()

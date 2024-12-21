import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    print("\nChecking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("Error: Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        print("\nTo fix:")
        print("1. Download Python 3.11+ from python.org")
        print("2. During installation, check 'Add Python to PATH'")
        print("3. Restart VS Code completely")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")

def check_windows_requirements():
    if sys.platform == 'win32':
        print("\nChecking Windows-specific requirements...")
        try:
            import _msi
            print("✓ Visual C++ Build Tools appear to be installed")
        except ImportError:
            print("\nWarning: Visual C++ Build Tools not detected")
            print("\nPlease install the Visual C++ Build Tools:")
            print("1. Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            print("2. Download and run the installer")
            print("3. Select 'Desktop development with C++'")
            print("4. Complete installation and restart VS Code")
            print("\nThis is required for building python-rtmidi")
            return False
    return True

def install_dependencies():
    print("\nInstalling required packages...")
    
    # Install numpy first as it's a dependency for other packages
    print("\nStep 1: Installing numpy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==2.2.0"])
        print("✓ numpy installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing numpy: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Try updating pip: python -m pip install --upgrade pip")
        print("3. If using VS Code, ensure the correct Python interpreter is selected")
        sys.exit(1)

    # Install sounddevice
    print("\nStep 2: Installing sounddevice...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice==0.5.1"])
        print("✓ sounddevice installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing sounddevice: {e}")
        print("\nTroubleshooting:")
        print("1. Check if PortAudio is installed")
        print("2. On Windows, try running VS Code as administrator")
        sys.exit(1)

    # Install python-rtmidi last as it requires build tools
    print("\nStep 3: Installing python-rtmidi...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-rtmidi==1.5.8"])
        print("✓ python-rtmidi installed successfully")
    except subprocess.CalledProcessError as e:
        if sys.platform == "win32":
            print("\nError: python-rtmidi installation failed")
            print("This usually means Visual C++ Build Tools are not installed or configured correctly")
            print("\nTo fix:")
            print("1. Close VS Code")
            print("2. Download Visual C++ Build Tools:")
            print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            print("3. Run the installer")
            print("4. Select 'Desktop development with C++'")
            print("5. Complete the installation")
            print("6. Restart your computer")
            print("7. Open VS Code and run this setup again")
        else:
            print(f"Error installing python-rtmidi: {e}")
            print("\nTroubleshooting:")
            print("1. Check if ALSA development files are installed (Linux)")
            print("2. Check if XCode command line tools are installed (macOS)")
        sys.exit(1)

def test_audio():
    print("\nTesting audio setup...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        default_device = sd.default.device[1]
        
        print("\nAudio device information:")
        print("------------------------")
        if default_device is not None:
            device = devices[default_device]
            print(f"Default output device: {device['name']}")
            print(f"Channels: {device['max_output_channels']}")
            print(f"Sample rate: {device['default_samplerate']} Hz")
        else:
            print("No default audio device found")
            print("Please check your system's audio settings")
    except Exception as e:
        print(f"Audio device detection error: {e}")
        print("This might be normal if no audio devices are connected")

def test_midi():
    print("\nTesting MIDI setup...")
    try:
        import rtmidi
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        
        print("\nMIDI device information:")
        print("----------------------")
        if ports:
            print("Available MIDI input ports:")
            for i, port in enumerate(ports):
                print(f"[{i}] {port}")
        else:
            print("No MIDI devices detected")
            print("The synthesizer will use mock MIDI input")
    except Exception as e:
        print(f"MIDI detection error: {e}")
        print("This might be normal if no MIDI devices are connected")

def main():
    print("\nMIDI Synthesizer Setup")
    print("=====================")
    print("VS Code Environment Setup")
    
    # Check Python version first
    check_python_version()
    
    # Check Windows-specific requirements
    if sys.platform == 'win32':
        if not check_windows_requirements():
            sys.exit(1)
    
    # Install all dependencies
    install_dependencies()
    
    # Test audio and MIDI
    test_audio()
    test_midi()
    
    print("\nSetup completed successfully!")
    print("---------------------")
    print("Next steps:")
    print("1. If using VS Code:")
    print("   - Press Ctrl+Shift+P")
    print("   - Type 'Python: Select Interpreter'")
    print("   - Choose the interpreter from your project")
    print("\n2. Run the synthesizer:")
    print("   python synth.py")
    
    if sys.platform == 'win32':
        print("\nNote for Windows users:")
        print("If you don't hear any sound:")
        print("1. Check Windows sound settings")
        print("2. Make sure your audio device is set as default")
        print("3. Try running VS Code as administrator")

if __name__ == "__main__":
    main()

# MIDI Synthesizer

A polyphonic MIDI synthesizer with real-time audio processing capabilities, built in Python.

## Features
- Multiple waveform types (sine, sawtooth, triangle, pulse)
- ADSR envelope control
- Polyphonic voice management
- Real-time MIDI input processing
- Dynamic audio stream handling

## Prerequisites
- Python 3.11 or higher
- A MIDI keyboard (optional - the synthesizer includes a mock MIDI interface for testing)
- Audio output device

## Development Setup

### Prerequisites
1. Python 3.11 or higher
2. For Windows users:
   - Install [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Note: This is just the build tools, not Visual Studio IDE
   - During installation, select "Desktop development with C++" workload
   - This is required for building the python-rtmidi package
   - Visual Studio Code is recommended for development

### Installation Steps
1. Clone the repository
2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   # Windows users: Make sure you have installed Visual C++ Build Tools first
   pip install numpy==2.2.0
   pip install python-rtmidi==1.5.8
   pip install sounddevice==0.5.1
   ```

### Troubleshooting

#### Windows Installation Issues
If you see an error about "Microsoft Visual C++ 14.0 or greater is required":
1. Download Visual Studio Build Tools from the link above
2. Run the installer and select "Desktop development with C++"
3. Restart your terminal and try installing dependencies again

## Running the Synthesizer

1. Open the project in VS Code
2. Make sure your Python virtual environment is selected
3. Run the synthesizer:
   ```bash
   python synth.py
   ```

The synthesizer will automatically:
- Detect available MIDI input devices
- Fall back to a mock MIDI interface if no hardware is available
- Use the default audio output device
- Display debug information about MIDI events and voice status

## Testing without MIDI Hardware

The synthesizer includes a mock MIDI interface that simulates MIDI input. When no MIDI device is detected, it will automatically:
1. Initialize in mock mode
2. Run a test sequence demonstrating various features
3. Show MIDI event information in the console

## Controls

The following MIDI Control Change messages are supported:
- CC 73: Attack Time
- CC 74: Decay Time
- CC 75: Sustain Level
- CC 76: Release Time
- CC 77: Oscillator Type

## Troubleshooting

### No Audio Output
- Verify your system's default audio device is working
- Check if other applications can play audio
- The synthesizer will fall back to a null audio backend for testing if no audio device is available

### No MIDI Input
- Check if your MIDI device is connected and powered on
- Verify the device appears in your system's MIDI devices
- The synthesizer will use a mock MIDI interface if no hardware is detected

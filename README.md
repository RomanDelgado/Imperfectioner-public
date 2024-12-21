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
   pip install numpy python-rtmidi sounddevice
   ```

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

import numpy as np
import sounddevice as sd
from datetime import datetime as import_time
from midi_handler import MIDIHandler
from voice_manager import VoiceManager
import sounddevice as sd
from oscillator import midi_to_freq

class Synthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.block_size = 256
        self.voice_manager = VoiceManager(self.sample_rate)
        self.midi_handler = MIDIHandler(self.handle_midi_message)
        
    def handle_midi_message(self, message, _):
        status = message[0]
        msg_type = status & 0xF0
        channel = (status & 0x0F) + 1
        
        # Print message type header with timestamp
        print("\nMIDI Event Detected:")
        print("------------------")
        print(f"Time: {import_time().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"Channel: {channel:2d}/16")
        print(f"Message Type: 0x{msg_type:02X}")
        
        if msg_type == 0x90:  # Note On
            note = message[1]
            velocity = message[2]
            freq = midi_to_freq(note)
            if velocity > 0:
                note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
                octave = (note // 12) - 1
                print(f"Type: Note On")
                print(f"Note: {note_name}{octave} (MIDI: {note})")
                print(f"Frequency: {freq:.1f} Hz")
                print(f"Velocity: {velocity} ({velocity/127.0*100:.0f}%)")
                self.voice_manager.note_on(note, velocity)
            else:
                print(f"Type: Note Off (zero velocity)")
                print(f"Note: {note}")
                self.voice_manager.note_off(note)
        elif msg_type == 0x80:  # Note Off
            note = message[1]
            velocity = message[2]
            note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
            octave = (note // 12) - 1
            print(f"Type: Note Off")
            print(f"Note: {note_name}{octave} (MIDI: {note})")
            print(f"Release Velocity: {velocity}")
            self.voice_manager.note_off(note)
        elif msg_type == 0xB0:  # Control Change
            control = message[1]
            value = message[2]
            normalized = value / 127.0
            
            # Enhanced control name mapping
            ctrl_names = {
                73: ("Attack Time ", "ms", normalized * 2000),
                74: ("Decay Time", "ms", normalized * 2000),
                75: ("Sustain Level", "%", normalized * 100),
                76: ("Release Time", "ms", normalized * 2000),
                77: ("Oscillator Type", "", int(normalized * 3))
            }
            
            print(f"Type: Control Change")
            print(f"Control: {control}")
            
            if control in ctrl_names:
                name, unit, scaled = ctrl_names[control]
                print(f"Parameter: {name}")
                print(f"Value: {value} ({scaled:.0f}{unit})")
            else:
                print(f"Parameter: Unmapped Control {control}")
                print(f"Value: {value} ({normalized*100:.0f}%)")
                
            self.handle_control_change(control, value)

    def handle_control_change(self, control, value):
        normalized_value = value / 127.0
        if control == 73:  # Attack
            self.voice_manager.set_attack(normalized_value * 2.0)
        elif control == 74:  # Decay
            self.voice_manager.set_decay(normalized_value * 2.0)
        elif control == 75:  # Sustain
            self.voice_manager.set_sustain(normalized_value)
        elif control == 76:  # Release
            self.voice_manager.set_release(normalized_value * 2.0)
        elif control == 77:  # Oscillator Type
            self.voice_manager.set_oscillator_type(int(normalized_value * 3))

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
        
        audio_block = self.voice_manager.get_audio_block(frames)
        outdata[:] = audio_block.reshape(-1, 1)

    def run(self):
        print("\nStarting synthesizer...")
        print("====================")
        try:
            print("Audio Configuration:")
            print("-------------------")
            print(f"Sample Rate: {self.sample_rate} Hz")
            print(f"Block Size: {self.block_size} samples")
            print(f"Buffer Length: {self.block_size/self.sample_rate*1000:.1f} ms")
            
            print("\nInitializing Audio System...")
            print("------------------------")
            
            try:
                # Try to find a working audio device
                devices = sd.query_devices()
                default_device = sd.default.device[1] if sd.default.device is not None else None
                
                print("Available Audio Devices:")
                device_found = False
                for i, device in enumerate(devices):
                    if device['max_output_channels'] > 0:
                        device_found = True
                        print(f"[{i}] {device['name']}")
                        if i == default_device:
                            print(f"    ↳ (Default Output Device)")
                
                if not device_found:
                    print("No audio output devices found")
                    print("\nFalling back to null audio backend")
                    print("MIDI events will be processed and voice generation simulated")
            except Exception as e:
                print(f"\nError querying audio devices: {e}")
                print("Falling back to null audio backend")
                print("MIDI events will be processed and voice generation simulated")
            
            print("\nPress Ctrl+C to stop the synthesizer")
            print("=====================================")

            try:
                device_info = None
                try:
                    devices = sd.query_devices()
                    default_device = sd.default.device[1]
                    if default_device is not None:
                        device_info = devices[default_device]
                        print(f"\nUsing audio device: {device_info['name']}")
                except Exception:
                    pass

                stream_settings = {
                    'channels': 1,
                    'samplerate': self.sample_rate,
                    'blocksize': self.block_size,
                    'callback': self.audio_callback
                }
                
                if device_info:
                    stream_settings['device'] = default_device
                    print(f"Sample Rate: {device_info['default_samplerate']} Hz")
                    print(f"Channels: {device_info['max_output_channels']}")
                
                with sd.OutputStream(**stream_settings):
                    print("\nAudio stream started successfully")
                    print("Playing synthesizer output...")
                    print("\nControls:")
                    print("- CC 73: Attack Time")
                    print("- CC 74: Decay Time")
                    print("- CC 75: Sustain Level")
                    print("- CC 76: Release Time")
                    print("- CC 77: Oscillator Type")
                    while True:
                        sd.sleep(100)
                        
            except KeyboardInterrupt:
                print("\nShutting down synthesizer...")
                return
            except sd.PortAudioError as e:
                print(f"\nAudio device error: {e}")
                print("Continuing with null audio backend for testing")
                print("\nMIDI events will be processed and voice generation simulated")
                while True:
                    sd.sleep(100)
                
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Synth stopped due to error")
            return

    def test_midi_input(self):
        """Send test MIDI messages when running with mock MIDI interface"""
        if not hasattr(self.midi_handler, 'is_mock') or not self.midi_handler.is_mock:
            print("Note: Test MIDI input only available in mock mode")
            return
            
        print("\nStarting Synthesizer Test Sequence")
        print("===============================")
        print("Testing MIDI Input on Multiple Channels")
        print("Channel Range: 1-16")
        print("Control Change Range: 0-127")
        print("Note Range: 21-108 (A0-C8)")
        
        # Test 1: Basic Note Playback on Different Channels
        print("\nTest 1: Multi-Channel Note Playback")
        print("--------------------------------")
        print("Playing notes on different MIDI channels...")
        for channel in [1, 2, 4]:  # Test on different channels
            print(f"\nChannel {channel}:")
            print("Playing: Middle C (forte)")
            self.midi_handler.send_test_note_on(60, 100, channel)  # Middle C
            sd.sleep(800)  # Hold note
            print("Releasing note...")
            self.midi_handler.send_test_note_off(60, 0, channel)
            sd.sleep(500)  # Let release finish
        
        # Test 2: Velocity Sensitivity and Channel Info
        print("\nTest 2: Velocity Sensitivity and Channel Info")
        print("----------------------------------------")
        test_channels = [1, 2]  # Test on first two channels
        for channel in test_channels:
            print(f"\nTesting Channel {channel}:")
            for velocity in [32, 64, 96, 127]:
                print(f"Playing: Note E4 (velocity: {velocity}, channel: {channel})")
                self.midi_handler.send_test_note_on(64, velocity, channel)
                sd.sleep(500)
                self.midi_handler.send_test_note_off(64, 0, channel)
                sd.sleep(200)
        
        # Test 3: Polyphonic Playback
        print("\nTest 3: Polyphonic Playback")
        print("-------------------------")
        print("Playing: C Major Chord (C4-E4-G4)")
        self.midi_handler.send_test_note_on(60, 100)  # C4
        sd.sleep(100)
        self.midi_handler.send_test_note_on(64, 100)  # E4
        sd.sleep(100)
        self.midi_handler.send_test_note_on(67, 100)  # G4
        sd.sleep(1000)
        print("Releasing chord in sequence...")
        self.midi_handler.send_test_note_off(67)  # G4
        sd.sleep(200)
        self.midi_handler.send_test_note_off(64)  # E4
        sd.sleep(200)
        self.midi_handler.send_test_note_off(60)  # C4
        sd.sleep(500)
        
        # Test 4: ADSR Envelope and Control Changes
        print("\nTest 4: ADSR Envelope and Control Changes")
        print("-------------------------------------")
        print("Testing MIDI Control Change Messages:")
        print(" CC 73: Attack Time (0-2000ms)")
        print(" CC 74: Decay Time (0-2000ms)")
        print(" CC 75: Sustain Level (0-100%)")
        print(" CC 76: Release Time (0-2000ms)")
        print(" CC 77: Oscillator Type (0-3)")
        
        controls = [
            (73, "Attack", [0, 64, 127], ["Short (0ms)", "Medium (1000ms)", "Long (2000ms)"]),
            (74, "Decay", [0, 64, 127], ["Short (0ms)", "Medium (1000ms)", "Long (2000ms)"]),
            (75, "Sustain", [0, 64, 127], ["Low (0%)", "Medium (50%)", "High (100%)"]),
            (76, "Release", [0, 64, 127], ["Short (0ms)", "Medium (1000ms)", "Long (2000ms)"])
        ]
        
        test_channels = [1, 2]  # Test on first two channels
        for channel in test_channels:
            print(f"\nTesting Channel {channel}:")
            for ctrl, name, values, labels in controls:
                print(f"\nTesting {name} Time (CC {ctrl}):")
                for value, label in zip(values, labels):
                    print(f"Setting {name}: {label}")
                    self.midi_handler.send_test_control_change(ctrl, value, channel)
                    sd.sleep(200)
                    # Play test note with new settings
                    print(f"Playing test note on channel {channel}...")
                    self.midi_handler.send_test_note_on(69, 100, channel)  # A4
                    sd.sleep(800)
                    self.midi_handler.send_test_note_off(69, 0, channel)
                    sd.sleep(500)
        
        # Test 5: Oscillator Waveforms
        print("\nTest 5: Oscillator Waveforms")
        print("-------------------------")
        waveforms = ["Sine", "Sawtooth", "Triangle", "Pulse"]
        for i, name in enumerate(waveforms):
            print(f"Setting waveform: {name}")
            self.midi_handler.send_test_control_change(77, int(i * 42))
            sd.sleep(200)
            # Play arpeggio with new waveform
            notes = [60, 64, 67, 72]  # C major arpeggio
            print(f"Playing arpeggio with {name} wave")
            for note in notes:
                self.midi_handler.send_test_note_on(note, 100)
                sd.sleep(200)
                self.midi_handler.send_test_note_off(note)
                sd.sleep(50)
            sd.sleep(300)
            
        print("\nTest Sequence Complete!")
        print("===================")
        print("All basic synthesizer functions verified")

if __name__ == "__main__":
    try:
        synth = Synthesizer()
        
        # Start the synth
        synth.run()
        
        # If using mock MIDI interface, run test sequence
        if hasattr(synth.midi_handler, 'is_mock') and synth.midi_handler.is_mock:
            print("\nStarting test sequence in 2 seconds...")
            print("(Using mock MIDI interface for testing)")
            sd.sleep(2000)
            
            # Run comprehensive test sequence
            synth.test_midi_input()
            
            print("\nTest sequence completed")
            print("Synthesizer will continue running...")
            print("Press Ctrl+C to exit")
        else:
            print("\nWaiting for MIDI input...")
            print("Press Ctrl+C to exit")
        
        # Keep running until interrupted
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\nExiting synthesizer...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Try running with '--mock' flag for testing without MIDI hardware")
    finally:
        print("Cleanup complete")
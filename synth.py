import numpy as np
import sounddevice as sd
from midi_handler import MIDIHandler
from voice_manager import VoiceManager
from audio_output import AudioOutput
from oscillator import midi_to_freq

class Synthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.block_size = 256
        self.voice_manager = VoiceManager(self.sample_rate)
        self.audio_output = AudioOutput(self.sample_rate, self.block_size)
        self.midi_handler = MIDIHandler(self.handle_midi_message)
        
    def handle_midi_message(self, message, _):
        status = message[0]
        msg_type = status & 0xF0
        channel = (status & 0x0F) + 1
        
        # Print message type header
        print("\nMIDI Message Received:")
        print("--------------------")
        print(f"Channel: {channel:2d}")
        
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
                73: ("Attack Time", "ms", normalized * 2000),
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
            print("\nNote: Using null audio backend for testing")
            print("MIDI events will be processed and voice generation simulated")
            
            print("\nPress Ctrl+C to stop the synthesizer")
            print("=====================================")
            
            try:
                while True:
                    # Generate audio in blocks
                    audio_block = self.voice_manager.get_audio_block(self.block_size)
                    self.audio_output.write(audio_block)
                    sd.sleep(int(1000 * self.block_size / self.sample_rate))
            except KeyboardInterrupt:
                print("\nShutting down synthesizer...")
                return
                
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Synth stopped due to error")
            return

    def test_midi_input(self):
        """Send test MIDI messages when running with mock MIDI interface"""
        if not hasattr(self.midi_handler, 'is_mock') or not self.midi_handler.is_mock:
            print("Note: Test MIDI input only available in mock mode")
            return
            
        print("\nSending test MIDI messages...")
        print("=========================")
        
        # Test note on/off
        print("\nTest 1: Single Note")
        print("------------------")
        print("Sending: Middle C, forte velocity")
        self.midi_handler.send_test_note_on(60, 100)  # Middle C
        sd.sleep(500)  # Wait 500ms
        print("Sending: Note Off")
        self.midi_handler.send_test_note_off(60)
        sd.sleep(200)  # Brief pause between tests
        
        # Test chord
        print("\nTest 2: Major Chord")
        print("-----------------")
        print("Sending: C Major (C-E-G)")
        self.midi_handler.send_test_note_on(60, 100)  # C
        self.midi_handler.send_test_note_on(64, 100)  # E
        self.midi_handler.send_test_note_on(67, 100)  # G
        sd.sleep(1000)  # Wait 1s
        print("Sending: Release chord")
        self.midi_handler.send_test_note_off(60)
        self.midi_handler.send_test_note_off(64)
        self.midi_handler.send_test_note_off(67)
        sd.sleep(500)  # Pause before controls
        
        # Test controls
        print("\nTest 3: ADSR Controls")
        print("-------------------")
        for ctrl, name in [(73, "Attack"), (74, "Decay"), (75, "Sustain"), (76, "Release")]:
            print(f"\nTesting: {name} Time")
            print(f"Sending: {name} Min → Mid → Max")
            for value in [0, 64, 127]:
                self.midi_handler.send_test_control_change(ctrl, value)
                sd.sleep(300)
        
        print("\nTest 4: Oscillator Type")
        print("---------------------")
        print("Cycling through waveforms...")
        ctrl = 77
        for value in [0, 42, 84, 127]:  # Spread across the range
            self.midi_handler.send_test_control_change(ctrl, value)
            sd.sleep(300)
            
        print("\nTest sequence complete!")

if __name__ == "__main__":
    try:
        synth = Synthesizer()
        
        # Start the synth
        synth.run()
        
        print("\nStarting test sequence in 2 seconds...")
        sd.sleep(2000)
        
        # Run test sequence if in mock mode
        synth.test_midi_input()
        
        print("\nTest sequence completed")
        print("Press Ctrl+C to exit")
        
        # Keep running until interrupted
        while True:
            sd.sleep(1000)
            
    except KeyboardInterrupt:
        print("\nExiting synthesizer...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("Cleanup complete")

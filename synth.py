import numpy as np
import sounddevice as sd
from midi_handler import MIDIHandler
from voice_manager import VoiceManager
from audio_output import AudioOutput

class Synthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.block_size = 256
        self.voice_manager = VoiceManager(self.sample_rate)
        self.audio_output = AudioOutput(self.sample_rate, self.block_size)
        self.midi_handler = MIDIHandler(self.handle_midi_message)
        
    def handle_midi_message(self, message, _):
        msg_type = message[0] & 0xF0
        
        if msg_type == 0x90:  # Note On
            note = message[1]
            velocity = message[2]
            if velocity > 0:
                print(f"Note On: {note} (frequency: {midi_to_freq(note):.1f}Hz) velocity: {velocity}")
                self.voice_manager.note_on(note, velocity)
            else:
                print(f"Note Off (zero velocity): {note}")
                self.voice_manager.note_off(note)
        elif msg_type == 0x80:  # Note Off
            note = message[1]
            print(f"Note Off: {note}")
            self.voice_manager.note_off(note)
        elif msg_type == 0xB0:  # Control Change
            control = message[1]
            value = message[2]
            print(f"Control Change: {control} = {value}")
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
        try:
            # Main synth loop
            print("Synth is running. Press Ctrl+C to stop.")
            print("Note: Using null audio backend for testing - no sound output")
            print("MIDI events will still be processed and voice generation will work")
            
            try:
                while True:
                    # Generate audio in blocks
                    audio_block = self.voice_manager.get_audio_block(self.block_size)
                    self.audio_output.write(audio_block)
                    sd.sleep(int(1000 * self.block_size / self.sample_rate))
            except KeyboardInterrupt:
                print("\nStopping synth...")
                
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Synth stopped due to error")
            return

if __name__ == "__main__":
    synth = Synthesizer()
    synth.run()

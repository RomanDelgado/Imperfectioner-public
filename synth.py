import numpy as np
from datetime import datetime
from midi_handler import MIDIHandler
from voice_manager import VoiceManager
from audio_output import AudioOutput

class Synthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.block_size = 1024  # Increased block size
        self.voice_manager = VoiceManager(self.sample_rate)
        
        # Setup audio output with callback
        import sounddevice as sd
        def audio_callback(outdata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            try:
                audio_block = self.voice_manager.get_audio_block(frames)
                outdata[:] = audio_block.reshape(-1, 1)
            except Exception as e:
                print(f"Audio callback error: {e}")
                outdata.fill(0)
                
        self.stream = sd.OutputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype='float32',
            callback=audio_callback
        )
        self.stream.start()
        self.midi_handler = MIDIHandler(self.handle_midi_message)

    def handle_midi_message(self, message, _):
        status = message[0]
        msg_type = status & 0xF0
        channel = (status & 0x0F) + 1

        print(f"\nMIDI Event at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"Channel: {channel}")

        if msg_type == 0x90:  # Note On
            note = message[1]
            velocity = message[2]
            if velocity > 0:
                print(f"Note On: {note} velocity: {velocity}")
                self.voice_manager.note_on(note, velocity)
            else:
                print(f"Note Off: {note} (zero velocity)")
                self.voice_manager.note_off(note)
        elif msg_type == 0x80:  # Note Off
            note = message[1]
            print(f"Note Off: {note}")
            self.voice_manager.note_off(note)

    def run(self):
        print("\nStarting synthesizer...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                import time
                time.sleep(0.1)  # Just keep the main thread alive

        except KeyboardInterrupt:
            print("\nStopping synthesizer...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            print("Cleanup complete")

if __name__ == "__main__":
    synth = Synthesizer()

    # If using mock MIDI, run test sequence
    if hasattr(synth.midi_handler, 'is_mock') and synth.midi_handler.is_mock:
        print("\nRunning test sequence with mock MIDI input...")
        print("Playing a simple melody...")
            
        import time
        notes = [60, 64, 67, 72]  # C major chord ascending
        for note in notes:
            print(f"Playing note {note}...")
            synth.midi_handler.send_test_note_on(note, 100)
            time.sleep(0.5)
            synth.midi_handler.send_test_note_off(note)
            time.sleep(0.1)

    synth.run()
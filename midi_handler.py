import mido
from collections import deque

class MockMIDIInput:
    def __init__(self, callback):
        self.callback = callback

    def send_test_note_on(self, note, velocity=64):
        # Construct a note-on message (status byte 0x90)
        if self.callback:
            self.callback([0x90, note, velocity], None)

    def send_test_note_off(self, note):
        # Construct a note-off message (status byte 0x80)
        if self.callback:
            self.callback([0x80, note, 0], None)

class MIDIHandler:
    def __init__(self, callback):
        print("\nInitializing MIDI in mock mode (no hardware required)")
        self.midi_in = MockMIDIInput(callback)
        self.is_mock = True

    def send_test_note_on(self, note, velocity=64):
        self.midi_in.send_test_note_on(note, velocity)

    def send_test_note_off(self, note):
        self.midi_in.send_test_note_off(note)
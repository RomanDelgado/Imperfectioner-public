
import mido
from collections import deque

class MockMIDIInput:
    def __init__(self):
        self.callback = None
        self.message_queue = deque()
        
    def set_callback(self, callback):
        self.callback = callback
        
    def send_test_message(self, message):
        if self.callback:
            self.callback([message.status_byte, message.note, message.velocity], None)
            
    def send_note_on(self, note, velocity=64, channel=1):
        msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel-1)
        self.send_test_message(msg)
        
    def send_note_off(self, note, velocity=0, channel=1):
        msg = mido.Message('note_off', note=note, velocity=velocity, channel=channel-1)
        self.send_test_message(msg)
        
    def send_control_change(self, control, value, channel=1):
        msg = mido.Message('control_change', control=control, value=value, channel=channel-1)
        self.send_test_message(msg)

class MIDIHandler:
    def __init__(self, callback):
        self.callback = callback
        self.midi_in = MockMIDIInput()
        self.midi_in.set_callback(callback)
        self.is_mock = True
            
    def send_test_note_on(self, note, velocity=64, channel=1):
        if isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_on(note, velocity, channel)
            
    def send_test_note_off(self, note, velocity=0, channel=1):
        if isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_off(note, velocity, channel)
            
    def send_test_control_change(self, control, value, channel=1):
        if isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_control_change(control, value, channel)

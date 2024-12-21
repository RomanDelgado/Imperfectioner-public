
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
        self.midi_in = None
        self.port_name = None
        self.is_virtual = False
        self.is_mock = False
        
        print("\nInitializing MIDI System...")
        print("-------------------------")
        
        try:
            ports = mido.get_input_names()
            if ports:
                print(f"\nFound {len(ports)} MIDI input ports:")
                for i, port in enumerate(ports):
                    print(f"[{i}] {port}")
                self.midi_in = mido.open_input(ports[0], callback=self._mido_callback)
                self.port_name = ports[0]
                print(f"\nConnected to: {self.port_name}")
            else:
                print("\nNo MIDI ports found")
                print("Using mock MIDI interface for testing")
                self.midi_in = MockMIDIInput()
                self.midi_in.set_callback(callback)
                self.port_name = "Mock MIDI Interface"
                self.is_mock = True
        except Exception as e:
            print(f"\nError initializing MIDI: {e}")
            print("Using mock MIDI interface for testing")
            self.midi_in = MockMIDIInput()
            self.midi_in.set_callback(callback)
            self.port_name = "Mock MIDI Interface"
            self.is_mock = True
            
    def _mido_callback(self, msg):
        if msg.type == 'note_on':
            self.callback([0x90 | msg.channel, msg.note, msg.velocity], None)
        elif msg.type == 'note_off':
            self.callback([0x80 | msg.channel, msg.note, msg.velocity], None)
        elif msg.type == 'control_change':
            self.callback([0xB0 | msg.channel, msg.control, msg.value], None)
            
    def send_test_note_on(self, note, velocity=64, channel=1):
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_on(note, velocity, channel)
            
    def send_test_note_off(self, note, velocity=0, channel=1):
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_off(note, velocity, channel)
            
    def send_test_control_change(self, control, value, channel=1):
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_control_change(control, value, channel)
            
    def __del__(self):
        if hasattr(self, 'midi_in') and not self.is_mock:
            self.midi_in.close()

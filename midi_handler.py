import rtmidi
import sys
from collections import deque

class MockMIDIInput:
    """A mock MIDI input for testing when no MIDI system is available"""
    def __init__(self):
        self.callback = None
        self.message_queue = deque()
        
    def set_callback(self, callback):
        self.callback = callback
        
    def send_test_message(self, message):
        """Allow sending test MIDI messages"""
        if self.callback:
            self.callback(message, None)
            
    def send_note_on(self, note, velocity=64, channel=1):
        """Send a Note On message for testing"""
        status = 0x90 | ((channel - 1) & 0x0F)
        self.send_test_message([status, note & 0x7F, velocity & 0x7F])
        
    def send_note_off(self, note, velocity=0, channel=1):
        """Send a Note Off message for testing"""
        status = 0x80 | ((channel - 1) & 0x0F)
        self.send_test_message([status, note & 0x7F, velocity & 0x7F])
        
    def send_control_change(self, control, value, channel=1):
        """Send a Control Change message for testing"""
        status = 0xB0 | ((channel - 1) & 0x0F)
        self.send_test_message([status, control & 0x7F, value & 0x7F])

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
            self.midi_in = rtmidi.MidiIn()
            self.setup_midi()
        except (rtmidi.SystemError, RuntimeError) as e:
            print(f"\nWarning: Could not initialize MIDI hardware: {e}")
            print("Attempting to create virtual MIDI input...")
            
            # On Windows, we'll try to create a virtual port as a last resort
            if sys.platform == 'win32':
                try:
                    self.midi_in = rtmidi.MidiIn(rtmidi.API_WINDOWS_MM)
                    port_name = "Virtual MIDI Input"
                    print(f"Creating virtual port: {port_name}")
                    self.midi_in.open_virtual_port(port_name)
                    self.midi_in.set_callback(self.callback)
                    self.port_name = port_name
                    self.is_virtual = True
                    print("✓ Virtual port created successfully")
                except Exception as e:
                    print("\nNote: MIDI hardware and virtual ports unavailable")
                    print("Reason:", str(e))
                    print("Falling back to mock MIDI interface for testing")
                    self.midi_in = MockMIDIInput()
                    self.midi_in.set_callback(self.callback)
                    self.port_name = "Mock MIDI Interface"
                    self.is_mock = True
                    print("✓ Mock MIDI interface initialized")
            else:
                print("\nNote: MIDI hardware and virtual ports unavailable")
                print("Falling back to mock MIDI interface for testing")
                self.midi_in = MockMIDIInput()
                self.midi_in.set_callback(self.callback)
                self.port_name = "Mock MIDI Interface"
                self.is_mock = True
                print("✓ Mock MIDI interface initialized")
        
    def setup_midi(self):
        if not self.midi_in:
            print("Error: MIDI system not initialized")
            return
            
        if self.is_mock:
            print("\nMIDI Configuration:")
            print("-----------------")
            print("Mode: Mock MIDI Interface (Testing Mode)")
            print("Note: No hardware MIDI devices will be detected")
            print("      Use programmatic MIDI input for testing")
            return
            
        try:
            ports = self.midi_in.get_port_count()
            print("\nMIDI Port Status:")
            print("----------------")
            
            if ports:
                print(f"Found {ports} hardware MIDI input port{'s' if ports > 1 else ''}:")
                for i in range(ports):
                    port_name = self.midi_in.get_port_name(i)
                    print(f"  [{i}] {port_name}")
                    if i == 0:  # Mark default port
                        print("      ↳ (Default Input Port)")
                
                try:
                    default_port = 0
                    port_name = self.midi_in.get_port_name(default_port)
                    print(f"\nConnecting to MIDI port {default_port}: {port_name}")
                    self.midi_in.open_port(default_port)
                    self.port_name = port_name
                    print("✓ Connection established successfully")
                except Exception as e:
                    print(f"\nError connecting to MIDI port: {e}")
                    print("Falling back to virtual MIDI input...")
                    self.midi_in.open_virtual_port("Virtual Input")
                    self.port_name = "Virtual Input"
                    self.is_virtual = True
            else:
                print("No hardware MIDI ports detected")
                print("Creating virtual MIDI input port 'Virtual Input'")
                self.midi_in.open_virtual_port("Virtual Input")
                self.port_name = "Virtual Input"
                self.is_virtual = True
                print("✓ Virtual port created successfully")
                
            print("\nMIDI Configuration:")
            print("-----------------")
            print(f"Active Port: {self.port_name}")
            print(f"Mode: {'Virtual' if self.is_virtual else 'Hardware'}")
            
        except Exception as e:
            print(f"\nError during MIDI setup: {e}")
            print("MIDI functionality may be limited")
            
        print("\nReady for MIDI input - waiting for messages...")
        self.midi_in.set_callback(self.callback)
        
    def send_test_note_on(self, note, velocity=64, channel=1):
        """Send a test Note On message when in mock mode"""
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_on(note, velocity, channel)
            
    def send_test_note_off(self, note, velocity=0, channel=1):
        """Send a test Note Off message when in mock mode"""
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_note_off(note, velocity, channel)
            
    def send_test_control_change(self, control, value, channel=1):
        """Send a test Control Change message when in mock mode"""
        if self.is_mock and isinstance(self.midi_in, MockMIDIInput):
            self.midi_in.send_control_change(control, value, channel)
            
    def __del__(self):
        if hasattr(self, 'midi_in') and self.midi_in:
            try:
                self.midi_in.close_port()
            except Exception:
                pass

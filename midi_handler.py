import rtmidi
import sys

class MIDIHandler:
    def __init__(self, callback):
        self.callback = callback
        self.midi_in = None
        try:
            self.midi_in = rtmidi.MidiIn()
            self.setup_midi()
        except (rtmidi.SystemError, RuntimeError) as e:
            print(f"Warning: Could not initialize MIDI: {e}")
            print("Running in virtual MIDI mode - no hardware MIDI input available")
            try:
                # Try to create a virtual port as fallback
                self.midi_in = rtmidi.MidiIn()
                self.midi_in.open_virtual_port("Virtual Input")
                self.midi_in.set_callback(self.callback)
            except Exception as e:
                print(f"Could not create virtual MIDI port: {e}")
                print("MIDI functionality will be limited")
        
    def setup_midi(self):
        if not self.midi_in:
            return
            
        ports = self.midi_in.get_port_count()
        if ports:
            print("Available MIDI ports:")
            for i in range(ports):
                print(f"{i}: {self.midi_in.get_port_name(i)}")
            self.midi_in.open_port(0)
        else:
            print("No MIDI ports available. Opening virtual port.")
            self.midi_in.open_virtual_port("Virtual Input")
            
        self.midi_in.set_callback(self.callback)
        
    def __del__(self):
        if hasattr(self, 'midi_in') and self.midi_in:
            try:
                self.midi_in.close_port()
            except Exception:
                pass

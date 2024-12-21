import numpy as np
from oscillator import Oscillator, midi_to_freq
from envelope import ADSREnvelope

class Voice:
    def __init__(self, sample_rate):
        self.oscillator = Oscillator(sample_rate)
        self.envelope = ADSREnvelope(sample_rate)
        self.note = None
        self.velocity = 0
        self.active = False
        
    def note_on(self, note, velocity):
        self.note = note
        self.velocity = velocity / 127.0
        self.oscillator.set_frequency(midi_to_freq(note))
        self.envelope.note_on()
        self.active = True
        
    def note_off(self):
        self.envelope.note_off()
        
    def is_active(self):
        return self.active and self.envelope.state != 'idle'
        
    def generate_samples(self, num_samples):
        if not self.active:
            return np.zeros(num_samples)
            
        samples = self.oscillator.get_samples(num_samples)
        envelope = self.envelope.get_envelope(num_samples)
        
        if not self.is_active():
            self.active = False
            
        return samples * envelope * self.velocity

class VoiceManager:
    def __init__(self, sample_rate, max_voices=16):
        self.voices = [Voice(sample_rate) for _ in range(max_voices)]
        self.sample_rate = sample_rate
        self._last_active_count = 0  # For tracking voice count changes
        
    def note_on(self, note, velocity):
        # First try to find an inactive voice
        voice = next((v for v in self.voices if not v.is_active()), None)
        
        # If no inactive voice, use the oldest one
        if voice is None:
            voice = self.voices[0]
            # Rotate voices to maintain age order
            self.voices = self.voices[1:] + [self.voices[0]]
            
        voice.note_on(note, velocity)
        
    def note_off(self, note):
        for voice in self.voices:
            if voice.note == note:
                voice.note_off()
                
    def get_audio_block(self, num_samples):
        # Mix all active voices
        mixed = np.zeros(num_samples)
        active_voices = 0
        active_notes = []
        
        for voice in self.voices:
            if voice.is_active():
                mixed += voice.generate_samples(num_samples)
                active_voices += 1
                note = voice.note
                note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
                octave = (note // 12) - 1
                active_notes.append(f"{note_name}{octave}")
                
        # Prevent clipping by normalizing based on voice count
        if active_voices > 0:
            mixed /= max(1, np.sqrt(active_voices))
            if len(active_notes) != self._last_active_count:
                print("\nVoice Status Update:")
                print("-----------------")
                print(f"Active Voices: {active_voices}")
                print(f"Notes Playing: {', '.join(sorted(active_notes))}")
                print(f"Voice Usage: {active_voices}/{len(self.voices)} ({active_voices/len(self.voices)*100:.0f}%)")
                print(f"Voice Allocation:")
                print(f"Voice Allocation:")
                for i, voice in enumerate(self.voices):
                    if voice.is_active():
                        note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][voice.note % 12]
                        octave = (voice.note // 12) - 1
                        print(f"  Voice {i:2d}: {note_name}{octave} (MIDI: {voice.note}, Velocity: {voice.velocity*127:.0f})")
                self._last_active_count = len(active_notes)
            
        return mixed
        
    def set_attack(self, value):
        for voice in self.voices:
            voice.envelope.set_attack(value)
            
    def set_decay(self, value):
        for voice in self.voices:
            voice.envelope.set_decay(value)
            
    def set_sustain(self, value):
        for voice in self.voices:
            voice.envelope.set_sustain(value)
            
    def set_release(self, value):
        for voice in self.voices:
            voice.envelope.set_release(value)
            
    def set_oscillator_type(self, type_idx):
        for voice in self.voices:
            voice.oscillator.set_type(type_idx)

import numpy as np

class Oscillator:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.phase = 0
        self.freq = 440.0
        self.types = ['sine', 'sawtooth', 'triangle', 'pulse']
        self.current_type = 0

    def set_frequency(self, freq):
        self.freq = freq

    def set_type(self, type_idx):
        self.current_type = type_idx % len(self.types)

    def get_samples(self, num_samples):
        phase_increment = 2.0 * np.pi * self.freq / self.sample_rate
        phases = np.linspace(self.phase,
                           self.phase + phase_increment * num_samples,
                           num_samples, endpoint=False)
        
        if self.types[self.current_type] == 'sine':
            samples = np.sin(phases)
        elif self.types[self.current_type] == 'sawtooth':
            samples = 2.0 * (phases / (2.0 * np.pi) - np.floor(0.5 + phases / (2.0 * np.pi)))
        elif self.types[self.current_type] == 'triangle':
            samples = 2.0 * np.abs(2.0 * (phases / (2.0 * np.pi) - np.floor(0.5 + phases / (2.0 * np.pi)))) - 1.0
        else:  # pulse
            samples = np.where(np.sin(phases) >= 0, 1.0, -1.0)

        self.phase = phases[-1] + phase_increment
        self.phase %= 2.0 * np.pi
        
        return samples

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

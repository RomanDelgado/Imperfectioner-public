import numpy as np

class ADSREnvelope:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.attack = 0.1  # seconds
        self.decay = 0.1   # seconds
        self.sustain = 0.7 # level (0-1)
        self.release = 0.2 # seconds
        
        self.current_level = 0.0
        self.state = 'idle'
        self.samples_processed = 0
        
    def set_attack(self, attack_time):
        self.attack = max(0.001, attack_time)
        
    def set_decay(self, decay_time):
        self.decay = max(0.001, decay_time)
        
    def set_sustain(self, sustain_level):
        self.sustain = np.clip(sustain_level, 0.0, 1.0)
        
    def set_release(self, release_time):
        self.release = max(0.001, release_time)
        
    def note_on(self):
        self.state = 'attack'
        self.samples_processed = 0
        
    def note_off(self):
        self.state = 'release'
        self.samples_processed = 0
        
    def get_envelope(self, num_samples):
        envelope = np.zeros(num_samples)
        current_sample = 0
        
        while current_sample < num_samples:
            if self.state == 'idle':
                envelope[current_sample:] = 0.0
                break
                
            elif self.state == 'attack':
                attack_samples = int(self.attack * self.sample_rate)
                remaining = attack_samples - self.samples_processed
                samples_to_process = min(remaining, num_samples - current_sample)
                
                t = np.linspace(self.current_level,
                              1.0,
                              samples_to_process + 1)[:-1]
                envelope[current_sample:current_sample + samples_to_process] = t
                
                self.samples_processed += samples_to_process
                current_sample += samples_to_process
                self.current_level = t[-1] if len(t) > 0 else self.current_level
                
                if self.samples_processed >= attack_samples:
                    self.state = 'decay'
                    self.samples_processed = 0
                    
            elif self.state == 'decay':
                decay_samples = int(self.decay * self.sample_rate)
                remaining = decay_samples - self.samples_processed
                samples_to_process = min(remaining, num_samples - current_sample)
                
                t = np.linspace(self.current_level,
                              self.sustain,
                              samples_to_process + 1)[:-1]
                envelope[current_sample:current_sample + samples_to_process] = t
                
                self.samples_processed += samples_to_process
                current_sample += samples_to_process
                self.current_level = t[-1] if len(t) > 0 else self.current_level
                
                if self.samples_processed >= decay_samples:
                    self.state = 'sustain'
                    
            elif self.state == 'sustain':
                samples_to_process = num_samples - current_sample
                envelope[current_sample:] = self.sustain
                current_sample = num_samples
                self.current_level = self.sustain
                
            elif self.state == 'release':
                release_samples = int(self.release * self.sample_rate)
                remaining = release_samples - self.samples_processed
                samples_to_process = min(remaining, num_samples - current_sample)
                
                t = np.linspace(self.current_level,
                              0.0,
                              samples_to_process + 1)[:-1]
                envelope[current_sample:current_sample + samples_to_process] = t
                
                self.samples_processed += samples_to_process
                current_sample += samples_to_process
                self.current_level = t[-1] if len(t) > 0 else self.current_level
                
                if self.samples_processed >= release_samples:
                    self.state = 'idle'
                    
        return envelope

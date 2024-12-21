import numpy as np
from collections import deque
import sounddevice as sd

class NullAudioBackend:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.is_running = False
        
    def start(self):
        print("Starting null audio backend (no audio output)")
        self.is_running = True
        
    def stop(self):
        self.is_running = False
        
    def write(self, samples):
        pass  # Discard samples in null backend

class AudioOutput:
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.buffer = deque(maxlen=block_size * 4)  # Increased buffer size for stability
        self.backend = None
        self.setup_audio()
        
    def setup_audio(self):
        try:
            # Try to find a working audio device
            devices = sd.query_devices()
            default_device = sd.default.device[1] if sd.default.device is not None else None
            
            # Check if we have a valid output device
            if default_device is not None and default_device >= 0:
                device_info = devices[default_device]
                if device_info['max_output_channels'] > 0:
                    print(f"Using audio device: {device_info['name']}")
                    return
                    
            # No valid audio device found, use null backend
            print("No valid audio device found, using null audio backend")
            self.backend = NullAudioBackend(self.sample_rate)
            self.backend.start()
            
        except Exception as e:
            print(f"Audio device error: {e}")
            print("Falling back to null audio backend")
            self.backend = NullAudioBackend(self.sample_rate)
            self.backend.start()
    
    def write(self, samples):
        if self.backend:
            self.backend.write(samples)
        else:
            self.buffer.extend(samples)
        
    def read(self, num_samples):
        if self.backend:
            return np.zeros(num_samples)  # Null backend always returns silence
            
        if len(self.buffer) < num_samples:
            # If not enough samples, pad with zeros
            padding = np.zeros(num_samples - len(self.buffer))
            output = np.array([self.buffer.popleft() for _ in range(len(self.buffer))])
            return np.concatenate([output, padding])
        
        output = np.array([self.buffer.popleft() for _ in range(num_samples)])
        return output
        
    def __del__(self):
        if self.backend:
            self.backend.stop()

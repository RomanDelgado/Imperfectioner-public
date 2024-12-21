import numpy as np
from collections import deque
import sounddevice as sd

class NullAudioBackend:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.is_running = False
        self.samples_written = 0
        self.peak_level = 0.0
        
    def start(self):
        print("Starting null audio backend (no audio output)")
        print("Audio will be simulated for testing purposes")
        self.is_running = True
        
    def stop(self):
        print("\nNull Audio Backend Statistics:")
        print("---------------------------")
        print(f"Total samples processed: {self.samples_written}")
        print(f"Duration: {self.samples_written / self.sample_rate:.1f} seconds")
        print(f"Peak level: {self.peak_level:.1%}")
        self.is_running = False
        
    def write(self, samples):
        self.samples_written += len(samples)
        if len(samples) > 0:
            self.peak_level = max(self.peak_level, np.max(np.abs(samples)))

class AudioOutput:
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.buffer = deque(maxlen=block_size * 4)  # Increased buffer size for stability
        self.backend = None
        self.setup_audio()
        
    def setup_audio(self):
        try:
            print("\nAudio System Configuration")
            print("=======================")
            print(f"Sample Rate: {self.sample_rate} Hz")
            print(f"Block Size: {self.block_size} samples")
            print(f"Block Duration: {self.block_size/self.sample_rate*1000:.1f} ms")
            print(f"Buffer Size: {self.buffer.maxlen} samples")
            print(f"Buffer Duration: {self.buffer.maxlen/self.sample_rate*1000:.1f} ms")
            
            try:
                # Try to find a working audio device
                try:
                    devices = sd.query_devices()
                    default_device = sd.default.device[1] if sd.default.device is not None else None
                    
                    print("\nAvailable Audio Devices:")
                    device_found = False
                    for i, device in enumerate(devices):
                        if device['max_output_channels'] > 0:
                            device_found = True
                            print(f"[{i}] {device['name']}")
                    
                    if not device_found:
                        print("No audio output devices found")
                        raise sd.PortAudioError("No audio output devices available")
                except Exception as e:
                    print(f"\nError querying audio devices: {e}")
                    raise

                # Check if we have a valid output device
                if default_device is not None and default_device >= 0:
                    device_info = devices[default_device]
                    if device_info['max_output_channels'] > 0:
                        print("\nAudio Device Information:")
                        print("----------------------")
                        print(f"Device Name: {device_info['name']}")
                        print(f"Channels: {device_info['max_output_channels']}")
                        print(f"Default Sample Rate: {device_info['default_samplerate']} Hz")
                        return
                        
                # No valid audio device found, use null backend
                print("\nNo valid audio device found")
                print("Using null audio backend for testing")
                self.backend = NullAudioBackend(self.sample_rate)
                self.backend.start()
                
            except Exception as e:
                print(f"\nAudio device error: {e}")
                print("Using null audio backend for testing")
                self.backend = NullAudioBackend(self.sample_rate)
                self.backend.start()
                
        except Exception as e:
            print(f"\nFatal audio system error: {e}")
            raise
    
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

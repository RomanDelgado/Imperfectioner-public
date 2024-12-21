import numpy as np
from collections import deque
import sounddevice as sd
import sys
import time

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
        self.buffer = deque(maxlen=block_size * 8)  # Increased buffer size for stability
        self.backend = None
        self.stream = None
        self.setup_audio()
        
    def setup_audio(self):
        print("\nAudio System Configuration")
        print("=======================")
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Block Size: {self.block_size} samples")
        print(f"Block Duration: {self.block_size/self.sample_rate*1000:.1f} ms")
        print(f"Buffer Size: {self.buffer.maxlen} samples")
        print(f"Buffer Duration: {self.buffer.maxlen/self.sample_rate*1000:.1f} ms")
        
        try:
            # Try to initialize sounddevice with a small timeout
            sd._terminate()
            time.sleep(0.1)  # Give time for cleanup
            sd._initialize()
            
            # Get host APIs first
            try:
                host_apis = sd.query_hostapis()
                if sys.platform == 'win32':
                    print("\nConfiguring Windows Audio System...")
                    print("-----------------------------")
                    
                    wasapi_found = False
                    dsound_found = False
                    
                    for i, api in enumerate(host_apis):
                        api_name = api['name'].upper()
                        print(f"[{i}] {api['name']}")
                        if 'WASAPI' in api_name:
                            print("    ↳ (Recommended for low latency)")
                            wasapi_found = True
                        elif 'DIRECTSOUND' in api_name:
                            print("    ↳ (Most compatible)")
                            dsound_found = True
                            
                    if not (wasapi_found or dsound_found):
                        print("\nWarning: No Windows audio APIs detected")
                        print("Please ensure Windows audio services are running:")
                        print("1. Press Win+R, type 'services.msc'")
                        print("2. Find 'Windows Audio' and 'Windows Audio Endpoint Builder'")
                        print("3. Ensure both are set to 'Automatic' and are running")
                else:
                    print("\nAvailable Audio APIs:")
                    print("------------------")
                    for i, api in enumerate(host_apis):
                        print(f"[{i}] {api['name']}")
                        if sys.platform == 'darwin' and api['name'] == 'CoreAudio':
                            print("    ↳ (Recommended for macOS)")
                        elif sys.platform == 'linux' and api['name'] == 'ALSA':
                            print("    ↳ (Recommended for Linux)")
                            
            except Exception as e:
                print(f"\nWarning: Could not query audio APIs: {e}")
                if sys.platform == 'win32':
                    print("\nTroubleshooting Windows Audio:")
                    print("1. Check Windows audio services")
                    print("2. Verify audio drivers are installed")
                    print("3. Try running VS Code as administrator")
                
            # Query available devices
            try:
                devices = sd.query_devices()
                if devices is None:
                    raise RuntimeError("No audio devices found")
                
                print("\nDetected Audio Devices:")
                print("--------------------")
                
                # Get default device first
                default_device = None
                try:
                    default_device = sd.default.device[1]
                    if default_device is not None:
                        device_info = devices[default_device]
                        print(f"\nDefault Output Device:")
                        print(f"- Name: {device_info['name']}")
                        print(f"- Sample Rate: {device_info['default_samplerate']:.0f} Hz")
                        print(f"- Channels: {device_info['max_output_channels']}")
                except Exception as e:
                    print(f"\nWarning: Could not get default device: {e}")
                
                # List all output devices
                output_devices = []
                for i, device in enumerate(devices):
                    try:
                        if device['max_output_channels'] > 0:
                            output_devices.append((i, device))
                            print(f"\nDevice [{i}]:")
                            print(f"- Name: {device['name']}")
                            print(f"- Channels: {device['max_output_channels']}")
                            print(f"- Sample Rate: {device['default_samplerate']:.0f} Hz")
                            is_default = i == default_device
                            if is_default:
                                print("  ↳ (Default Output Device)")
                    except Exception as e:
                        print(f"Warning: Could not query device {i}: {e}")
                
                if not output_devices:
                    print("\nNo audio output devices found")
                    print("Falling back to null audio backend")
                    self.backend = NullAudioBackend(self.sample_rate)
                    self.backend.start()
                    return
                
                # Try to use default device first
                if default_device is not None:
                    try:
                        # Attempt to open a test stream
                        test_stream = sd.OutputStream(
                            device=default_device,
                            channels=1,
                            samplerate=self.sample_rate,
                            blocksize=self.block_size
                        )
                        test_stream.start()
                        test_stream.stop()
                        test_stream.close()
                        
                        print(f"\nSuccessfully initialized audio output:")
                        print(f"Using device: {devices[default_device]['name']}")
                        return
                    except Exception as e:
                        print(f"\nCould not use default device: {e}")
                
                # Try other devices if default failed
                for device_idx, device_info in output_devices:
                    try:
                        print(f"\nTrying device: {device_info['name']}")
                        test_stream = sd.OutputStream(
                            device=device_idx,
                            channels=1,
                            samplerate=self.sample_rate,
                            blocksize=self.block_size
                        )
                        test_stream.start()
                        test_stream.stop()
                        test_stream.close()
                        
                        print(f"Successfully initialized audio output")
                        print(f"Using device: {device_info['name']}")
                        return
                    except Exception as e:
                        print(f"Could not use device: {e}")
                        continue
                
                print("\nNo working audio devices found")
                print("Falling back to null audio backend")
                self.backend = NullAudioBackend(self.sample_rate)
                self.backend.start()
                
            except Exception as e:
                print(f"\nError scanning audio devices: {e}")
                print("Falling back to null audio backend")
                self.backend = NullAudioBackend(self.sample_rate)
                self.backend.start()
                
        except Exception as e:
            print(f"\nFatal audio system error: {e}")
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
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            
        if self.backend:
            try:
                self.backend.stop()
            except:
                pass

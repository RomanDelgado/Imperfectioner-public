import numpy as np
from collections import deque
import sounddevice as sd
import sys

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
                    # Get host APIs first
                    if sys.platform == 'win32':
                        print("\nConfiguring Windows Audio System...")
                        print("-----------------------------")
                        try:
                            host_apis = sd.query_hostapis()
                            recommended_apis = ['WASAPI', 'DirectSound']
                            print("\nAvailable Audio APIs:")
                            print("------------------")
                            for i, api in enumerate(host_apis):
                                print(f"[{i}] {api['name']}")
                                if api['name'] in recommended_apis:
                                    print("    ↳ (Recommended for Windows)")
                                    if api['name'] == 'WASAPI':
                                        print("       Best for low latency")
                                    elif api['name'] == 'DirectSound':
                                        print("       Most compatible")
                        except Exception as e:
                            print("\nWarning: Could not query Windows audio APIs")
                            print(f"Error: {e}")
                            print("\nTroubleshooting steps:")
                            print("1. Check Windows audio settings")
                            print("2. Verify audio drivers are installed")
                            print("3. Try running VS Code as administrator")
                            raise
                    else:
                        # Non-Windows platforms
                        host_apis = sd.query_hostapis()
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
                    print("This might be because:")
                    print("- Audio subsystem is not initialized")
                    print("- No audio drivers are installed")
                    
                # Query devices with better error handling
                try:
                    devices = sd.query_devices()
                    if devices is None:
                        raise sd.PortAudioError("No audio devices found")
                    
                    if sys.platform == 'win32':
                        print("\nWindows Audio Devices:")
                        print("-------------------")
                        default_device = None
                        try:
                            default_device = sd.default.device[1]
                            if default_device is not None:
                                device_info = devices[default_device]
                                print(f"Default Output: {device_info['name']}")
                                print(f"Sample Rate: {device_info['default_samplerate']:.0f} Hz")
                                print(f"Channels: {device_info['max_output_channels']}")
                        except Exception as default_error:
                            print("\nWarning: Could not detect default audio device")
                            print("Please check Windows Sound settings")
                    else:
                        default_device = sd.default.device[1] if sd.default.device is not None else None
                        
                except Exception as e:
                    if sys.platform == 'win32':
                        print("\nError: Windows Audio Device Detection Failed")
                        print("---------------------------------")
                        print("Common Solutions:")
                        print("1. Check Windows Sound settings:")
                        print("   - Right-click speaker icon → Sound settings")
                        print("   - Verify output device is selected and working")
                        print("\n2. Check Device Manager:")
                        print("   - Open Device Manager")
                        print("   - Look for errors under 'Sound, video and game controllers'")
                        print("   - Update or reinstall audio drivers if needed")
                        print("\n3. Try running as administrator:")
                        print("   - Close VS Code")
                        print("   - Right-click VS Code → Run as administrator")
                        print("   - Try running the synthesizer again")
                    else:
                        print(f"\nError querying audio devices: {e}")
                        print("This might be because:")
                        print("- Audio drivers are not installed")
                        print("- The system has no audio devices")
                        print("- Permission issues")
                    raise
                
                print("\nScanning Audio Devices:")
                print("--------------------")
                output_devices = []
                
                for i, device in enumerate(devices):
                    try:
                        if device['max_output_channels'] > 0:
                            output_devices.append((i, device))
                            print(f"\nDevice [{i}]: {device['name']}")
                            if i == default_device:
                                print("    ↳ Default Output Device")
                            print(f"    API: {device.get('hostapi', 'Unknown')}")
                            print(f"    Channels: {device['max_output_channels']}")
                            print(f"    Sample Rate: {device['default_samplerate']:.0f} Hz")
                            print(f"    Status: {'Active' if sd.check_output_settings(device=i, channels=1, samplerate=self.sample_rate) else 'Available'}")
                    except Exception as dev_err:
                        print(f"\nWarning: Could not query device {i}: {dev_err}")
                        continue
                
                if not output_devices:
                    print("\nNo usable audio output devices found")
                    print("Possible reasons:")
                    print("- No audio devices connected")
                    print("- Audio drivers not installed")
                    print("- Permission issues accessing audio devices")
                    print("\nFalling back to null audio backend for testing")
                    self.backend = NullAudioBackend(self.sample_rate)
                    self.backend.start()
                    return
                    
                # First try default device
                if default_device is not None and default_device >= 0:
                    try:
                        device_info = devices[default_device]
                        if device_info['max_output_channels'] > 0:
                            if sd.check_output_settings(device=default_device, channels=1, samplerate=self.sample_rate):
                                print(f"\nUsing default audio device: {device_info['name']}")
                                print(f"Sample Rate: {device_info['default_samplerate']:.0f} Hz")
                                print(f"Channels: {device_info['max_output_channels']}")
                                return
                    except Exception as e:
                        print(f"\nWarning: Could not use default device: {e}")
                
                # Try first available device
                for device_idx, device_info in output_devices:
                    try:
                        if sd.check_output_settings(device=device_idx, channels=1, samplerate=self.sample_rate):
                            print(f"\nUsing audio device: {device_info['name']}")
                            print(f"Sample Rate: {device_info['default_samplerate']:.0f} Hz")
                            print(f"Channels: {device_info['max_output_channels']}")
                            return
                    except Exception as e:
                        print(f"\nWarning: Could not use device {device_idx}: {e}")
                        continue
                
                print("\nNo working audio devices found")
                print("Falling back to null audio backend for testing")
                self.backend = NullAudioBackend(self.sample_rate)
                self.backend.start()
                
            except Exception as e:
                print(f"\nError during audio device scan: {e}")
                print("Falling back to null audio backend for testing")
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
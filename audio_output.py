import numpy as np
import sounddevice as sd
from collections import deque

class AudioOutput:
    def __init__(self, sample_rate=44100, block_size=256):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.stream = None
        self.setup_audio()

    def setup_audio(self):
        try:
            print("\nAudio Device Debug Information:")
            print("-----------------------------")
            
            # Force PortAudio to rescan devices
            sd._terminate()
            sd._initialize()
            
            devices = sd.query_devices()
            if devices is None or len(devices) == 0:
                raise sd.PortAudioError("No audio devices found on the system")
            
            print("\nAvailable audio devices:")
            print("----------------------")
            for idx, device in enumerate(devices):
                channels = device.get('max_output_channels', 0)
                name = device.get('name', 'Unknown')
                hostapi = device.get('hostapi', 0)
                print(f"[{idx}] {name}")
                print(f"    Channels: {channels}")
                print(f"    Host API: {sd.query_hostapis(hostapi)['name']}")
            
            # Try to get default output device
            try:
                default_device = None
                default_info = sd.query_devices(kind='output')
                if default_info is not None:
                    default_device = sd.default.device[1]  # Index 1 for output device
                print(f"\nDefault output device index: {default_device}")
            except Exception as e:
                print(f"Warning: Could not get default device: {e}")
                print("This might be because no audio devices are properly initialized")
                default_device = None
            
            # First try default device if available
            if default_device is not None:
                try:
                    device_info = devices[default_device]
                    print(f"\nAttempting to use default audio device:")
                    print(f"Name: {device_info['name']}")
                    print(f"Sample Rate: {device_info['default_samplerate']} Hz")
                    print(f"Output Channels: {device_info['max_output_channels']}")
                    
                    self.stream = sd.OutputStream(
                        device=default_device,
                        samplerate=self.sample_rate,
                        channels=1,
                        dtype=np.float32,
                        callback=None,  # No callback for direct writing
                        blocksize=self.block_size
                    )
                    self.stream.start()
                    print("\n✓ Audio output initialized successfully")
                    print(f"✓ Using device: {device_info['name']}")
                    print(f"✓ Sample rate: {self.sample_rate} Hz")
                    print(f"✓ Buffer size: {self.block_size} samples")
                    return
                except Exception as e:
                    print(f"\nWarning: Could not use default device:")
                    print(f"Error details: {str(e)}")
                    print("Will try other available devices...")
            
            # If default device failed, try each output device
            print("\nTrying alternative audio devices...")
            working_devices = []
            
            for idx, device in enumerate(devices):
                if device.get('max_output_channels', 0) > 0:
                    try:
                        print(f"\nTesting device: {device['name']}")
                        stream_test = sd.OutputStream(
                            device=idx,
                            samplerate=self.sample_rate,
                            channels=1,
                            dtype=np.float32,
                            callback=None,
                            blocksize=self.block_size
                        )
                        stream_test.start()
                        stream_test.stop()
                        stream_test.close()
                        working_devices.append((idx, device))
                        print(f"✓ Device {device['name']} is working")
                    except Exception as e:
                        print(f"✗ Device {device['name']} failed: {str(e)}")
                        continue
            
            if working_devices:
                # Use the first working device
                idx, device = working_devices[0]
                self.stream = sd.OutputStream(
                    device=idx,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype=np.float32,
                    callback=None,
                    blocksize=self.block_size
                )
                self.stream.start()
                print(f"\n✓ Successfully initialized audio:")
                print(f"  Device: {device['name']}")
                print(f"  Sample rate: {self.sample_rate} Hz")
                print(f"  Buffer size: {self.block_size} samples")
                return
            
            raise sd.PortAudioError("No working audio output devices found")
                    
        except Exception as e:
            print("\nAudio initialization failed!")
            print("-------------------------")
            print(f"Error: {str(e)}")
            print("\nTroubleshooting steps for VS Code:")
            print("1. Check Windows Sound settings")
            print("2. Verify your audio device is set as default")
            print("3. Try running VS Code as administrator")
            print("4. If using WSL, check WSL audio setup")
            print("\nRunning in silent mode for testing...")
            self.stream = None

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        try:
            # Clear the output buffer
            outdata.fill(0)
        except Exception as e:
            print(f"Audio callback error: {e}")

    def write(self, samples):
        if self.stream and self.stream.active:
            try:
                # Ensure samples are float32 and in correct shape
                samples = np.asarray(samples, dtype=np.float32)
                # Reshape to (frames, channels)
                samples = samples.reshape(-1, 1)
                # Write to stream directly
                self.stream.write(samples)
            except Exception as e:
                print(f"Audio write error: {e}")
                print(f"Sample shape: {samples.shape}, dtype: {samples.dtype}")

    def __del__(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass

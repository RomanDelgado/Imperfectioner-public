
import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'synth.py',
    '--onefile',
    '--name=midi_synth',
    '--add-data=oscillator.py:.',
    '--add-data=voice_manager.py:.',
    '--add-data=midi_handler.py:.',
    '--add-data=audio_output.py:.',
    '--add-data=envelope.py:.',
])

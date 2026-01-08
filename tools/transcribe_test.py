import wave
import struct
import requests
import os

OUT = os.path.join(os.path.dirname(__file__), 'test_silence.wav')

# Generate 1s silent WAV @16kHz, 16-bit mono
framerate = 16000
nframes = framerate * 1
with wave.open(OUT, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(framerate)
    silent_frame = struct.pack('<h', 0)
    wf.writeframes(silent_frame * nframes)

print('WAV written to', OUT)

import os

import sys

if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = os.environ.get('TRANSCRIBE_URL', 'http://localhost:8000/transcribe')
print('TARGET URL repr:', repr(url))
print('TARGET URL:', url)
with open(OUT, 'rb') as f:
    files = {'file': ('test_silence.wav', f, 'audio/wav')}
    try:
        resp = requests.post(url, files=files, timeout=30)
        print('Status:', resp.status_code)
        try:
            print('JSON:', resp.json())
        except Exception as e:
            print('Failed to decode JSON:', e)
            print('Text:', resp.text[:1000])
    except Exception as e:
        print('Request failed:', e)

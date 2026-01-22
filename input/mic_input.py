import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import sounddevice as sd
from scipy.io.wavfile import write
import uuid

SAMPLE_RATE = 16000
DURATION = 5  # seconds


def record_from_mic(duration=DURATION):
    """
    Records audio from microphone and saves to a temp wav file.
    """
    print(f"Recording for {duration} seconds... Speak now.")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    filename = f"temp_audio_{uuid.uuid4().hex}.wav"
    write(filename, SAMPLE_RATE, recording)

    print("Recording finished.")
    return filename

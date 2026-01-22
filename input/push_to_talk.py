import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import sounddevice as sd
from scipy.io.wavfile import write
import uuid
import numpy as np

SAMPLE_RATE = 16000


def push_to_talk():
    """
    Press ENTER to start recording.
    Press ENTER again to stop recording.
    """
    print("Press ENTER to start recording.")
    input()  # wait for enter (start)

    frames = []

    def callback(indata, frames_count, time, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback,
        dtype="int16"
    )

    stream.start()
    print("Recording... Press ENTER again to stop.")
    input()  # wait for enter (stop)

    stream.stop()
    stream.close()

    if not frames:
        raise RuntimeError("No audio captured.")

    audio = np.concatenate(frames, axis=0)

    filename = f"ptt_audio_{uuid.uuid4().hex}.wav"
    write(filename, SAMPLE_RATE, audio)

    print("Recording finished.")
    return filename

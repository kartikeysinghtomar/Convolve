import whisper

model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path, language="en")
    return result["text"].strip()

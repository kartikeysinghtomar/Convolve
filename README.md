# Convolve – Multimodal Government Scheme Discovery System

Convolve is a multimodal, explainable government scheme discovery system.
It allows users to find applicable schemes using text, voice, PDFs, and images,
while handling eligibility, exclusions, and uncertainty transparently.

## Features
- Semantic scheme search using Sentence Transformers + Qdrant
- Text, audio (Whisper), image & PDF input (OCR)
- Session memory with intent routing
- Semantic exclusion of inapplicable schemes
- State-aware filtering
- Explainability: why a scheme was shown or excluded

## Tech Stack
- Python 3.10+
- sentence-transformers (all-mpnet-base-v2)
- Qdrant (local)
- Whisper (audio transcription)
- Tesseract OCR (images & PDFs)

---

## Setup Instructions
### OCR Support (for image and pdf input support)

This project supports extracting text from images and PDFs using **Tesseract OCR**.
OCR is an add on feature and is **not required** to run the core system.

If Tesseract is not installed, the system will continue to work normally with
text and audio inputs and will simply skip OCR with a clear message.

To enable OCR:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt install tesseract-ocr`
- macOS: `brew install tesseract`


### Audio Input

Audio input uses the system microphone via `sounddevice` and Whisper.
This feature is add on and depends on system audio support.

If audio input is unavailable, the system will continue to work
normally with text and other mentioned inputs.

Whisper models are downloaded automatically on first use.



### 1. Clone the repository
```bash
git clone <your-repo-url>
cd convolve

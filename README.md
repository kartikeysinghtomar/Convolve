# Convolve
## Multimodal Government Scheme Discovery System

This is a **local, multimodal, explainable government scheme discovery system**.  
It helps users discover relevant government schemes using **text, voice, images, and PDFs**, while transparently explaining *why* a scheme was shown or excluded.

The system runs **entirely locally** using open-source tools and does **not depend on external APIs**.

---

## 1. What this system does

Most scheme discovery platforms rely on rigid filters and keyword matching. Convolve instead uses:

* **Semantic embeddings:** Meaning-based search rather than just keywords.
* **Session memory:** Tracks eligibility and exclusions throughout the chat.
* **Intent routing:** Categorizes inputs as positive, negative, or clarification.
* **Multimodal grounding:** Processes text, audio, PDFs, and images.
* **Recommends Schemes:** Recommends best suited government schemes for them.

* **Explainable reasoning:** Tells the user exactly why they qualify or don't.

The result is an **intelligent decision-support assistant**, not just a search engine.

---

## 2. Repository Structure

Your repository should be organized as follows:

```text
convolve/
│
├── test.py                     # MAIN ENTRY POINT
│
├── data/
│   └── ingestion/
│       ├── schemes.csv         # Scheme dataset (REQUIRED)
│       └── pdfs/               # Government PDFs for ingestion
│           └── *.pdf
│
├── db/
│   ├── qdrant_client.py
│   └── __init__.py
│
├── ingestion/
│   ├── ingest_schemes.py       # Reads data/ingestion/schemes.csv
│   ├── ingest_pdfs.py          # Reads PDFs from data/ingestion/pdfs/
│   └── __init__.py
│
├── retrieval/
│   ├── search.py
│   ├── search_docs.py
│   ├── search_user_docs.py
│   └── __init__.py
│
├── session/
│   ├── intent_router.py
│   ├── memory.py
│   └── __init__.py
│
├── input/
│   ├── upload_image.py
│   ├── upload_pdf.py
│   ├── audio_input.py
│   ├── mic_input.py
│   ├── push_to_talk.py
│   └── __init__.py
│
├── models/
│   ├── embeddings.py
│   └── __init__.py
│
├── explanations.py
├── requirements.txt
├── .gitignore
└── README.md

```
---

## 3. Prerequisites

3.1 Python (REQUIRED)

Compatible version : Python 3.10

#### Install Python 3.10 on Windows

    1. Go to: https://www.python.org/downloads/release/python-31013/
    2. Download the **Windows installer (64-bit)**.
    3. Run the installer.
    4. IMPORTANT: Check **“Add Python to PATH”**.
    5. Complete installation.

  Verify:

    python --version

#### Install Python 3.10 on macOS

Using Homebrew (recommended):

```bash
brew install python@3.10
```
  Verify:
    
    python3.10 --version

#### Install Python 3.10 on Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-distutils
```
Verify:

    python3.10 --version

  

3.2 Create a Virtual Environment (RECOMMENDED)

From the project root:

    python -m venv venv

Activate it:

    Windows: venv\Scripts\activate

    Linux / macOS: source venv/bin/activate

3.3 Install Python Dependencies
Bash

    pip install -r requirements.txt

Key libraries installed:   
```text
sentence-transformers, torch, qdrant-client, openai-whisper, sounddevice, pytesseract, and PyMuPDF.
```

## 4. Qdrant Setup (Local Mode)

This system uses Qdrant in Local Mode.

  >No Docker required: You do not need to run a server or visit localhost:6333.

  >How it works: The code creates a local folder named qdrant_storage/ in your project root and saves the data directly to the machine's disk.

>Data is stored locally in qdrant_data/.

## 5. Scheme Data Setup (REQUIRED)

#### 5.1 schemes.csv Location

Place your scheme dataset at: 
```
data/ingestion/
```
#### 5.2 Ingest Data

**IMPORTANT:** Run the following once to generate embeddings and store them in Qdrant:
Bash

    python ingestion/ingest_schemes.py

## 6. PDF Ingestion 

Place government PDFs inside:
```
data/ingestion/pdfs/
```
Run the ingestion script:
    
    python ingestion/ingest_pdfs.py

## 7. OCR Setup

> **Note:** OCR uses the system-installed Tesseract engine; it is intentionally not bundled with the repository to keep the project portable, secure, and cross-platform. If unavailable, OCR is skipped gracefully while all core features continue to work.

OCR enables reading images and scanned documents.

Install Tesseract OCR:

        Windows: Download from UB-Mannheim. Ensure "Add to PATH" is checked.

        Linux: sudo apt install tesseract-ocr

        macOS: brew install tesseract

    Note: Tesseract must be in your system PATH, not inside the project folder.

## 8. Audio Input Setup

    Uses the system microphone and Whisper for transcription.

    Note: Whisper models download automatically on first use. If a microphone is unavailable, the system defaults to text input.

## 9. Running the System

Start the interactive demo:

    py -3.10 test.py

>You can now enter text, use the microphone, upload documents, and ask for scheme recommendations.

## 10. Example Interaction

    User: i earn less than 50000

    System: Is this monthly or annual income?

    User: annual

    System: Eligibility context added. What schemes can benefit me?

## 11. Failure-Safe Behavior
Feature    Missing Dependency    Behavior
Text    None    Always works
OCR    Tesseract missing    Skipped with message
Audio    Mic/Backend missing    Skipped with message
Qdrant    Not running    Search unavailable
## 12. Full Capability Checklist

To run the model at full capacity:

    [ ] Python 3.10 installed

    [ ] Dependencies installed via requirements.txt

    [ ] Qdrant running (Local)

    [ ] schemes.csv present in ingestion folder

    [ ] Tesseract installed (for OCR)

    [ ] Microphone available (for Audio)

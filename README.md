# Convolve
## Intelligent Government Scheme Discovery System
This is a **local, multimodal, explainable government scheme discovery system**.  
It helps users discover relevant government schemes using **text, voice, images, and PDFs**, while transparently explaining *why* a scheme was shown or excluded.

The system runs **entirely locally** using open-source tools and does **not depend on external APIs**.

---

## 1. Key Features🚀

* 🧠 **Semantic Search:** Finds schemes based on *meaning*, not just keywords.
* 🎙️ **Multimodal Support:** Input data via **Text, Voice, Images (OCR), or PDFs**.
* 🔐 **Privacy First:** Runs **100% locally**. No external APIs, no data leaks.
* 💬 **Smart Session Memory:** Remembers your eligibility details (income, age) throughout the chat.
* ⚖️ **Explainable AI:** Don't just get a list of recommendations; understand exactly *why* you qualify or were excluded.

---

## 2. 📂 Project Structure

```text
📂convolve/
│
├── 📄test.py                     # MAIN ENTRY POINT
│
├── 📂data/
│   └── 📂ingestion/
│       ├── schemes.csv           # Scheme dataset (REQUIRED)
│       └── pdfs/                 # Government PDFs for ingestion
│           └── *.pdf
│
├── 📂db/
│   ├── 📄qdrant_client.py
│   └── 📄__init__.py
│
├── 📂ingestion/
│   ├── 📄ingest_schemes.py       # Reads data/ingestion/schemes.csv
│   ├── 📄ingest_pdfs.py          # Reads PDFs from data/ingestion/pdfs/
│   └── 📄__init__.py
│
├── 📂retrieval/
│   ├── 📄search.py
│   ├── 📄search_docs.py
│   ├── 📄search_user_docs.py
│   └── 📄__init__.py
│
├── 📂session/
│   ├── 📄intent_router.py
│   ├── 📄memory.py
│   └── 📄__init__.py
│
├── 📂input/
│   ├── 📄upload_image.py
│   ├── 📄upload_pdf.py
│   ├── 📄audio_input.py
│   ├── 📄mic_input.py
│   ├── 📄push_to_talk.py
│   └── 📄__init__.py
│
├── 📂models/
│   ├── 📄embeddings.py
│   └── 📄__init__.py
│
├── 📄explanations.py
├── requirements.txt
├── .gitignore
└── README.md

```
---

## 3. Prerequisites 🛠️

3.1 Python (REQUIRED)

Compatible version : Python 3.10

#### Install Python 3.10 on Windows

    1. Go to: https://www.python.org/downloads/release/python-31013/
    2. Download the **Windows installer (64-bit)**.
    3. Run the installer.
    4. IMPORTANT: Check **“Add Python to PATH”**.
    5. Complete installation.
>If you don't see an option to add Python to PATH:
>Search "Edit the system environment variables"
>
>In "Advanced"->"Environment Variable"->"System Variables"->"PATH"->"(Add path to Python 3.10.xx folder)"

Verify:

    py -3.10 --version


#### Install Python 3.10 on macOS

Using Homebrew (recommended):

```bash
brew install python@3.10
```


#### Install Python 3.10 on Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-distutils
```

  

3.2 Create a Virtual Environment (RECOMMENDED)

From the project root:

    py -3.10 -m venv venv

Activate it:

    Windows: 
    Terminal: venv\Scripts\activate
    PowerShell: .\venv\Scripts\Activate.ps1

    Linux / macOS: source venv/bin/activate

3.3 Install Python Dependencies
Bash

    pip install -r requirements.txt
>Recommendation: If the installation fails, try installing torch separately first: pip install torch --index-url https://download.pytorch.org/whl/torch/

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

    python -m ingestion.ingest_schemes

## 6. PDF Ingestion 

Place government PDFs inside:
```
data/ingestion/pdfs/
```
Run the ingestion script:
    
    python -m ingestion.ingest_pdfs

## 7. OCR Setup

> **Note:** OCR uses the system-installed Tesseract engine; it is intentionally not bundled with the repository to keep the project portable, secure, and cross-platform. If unavailable, OCR is skipped gracefully while all core features continue to work.

OCR enables reading images and scanned documents.

Install Tesseract OCR:

        Windows: Download from UB-Mannheim. Ensure "Add to PATH" is checked.

        Linux: sudo apt install tesseract-ocr

        macOS: brew install tesseract

    Note: Tesseract must be in your system PATH, not inside the project folder.
>If you don't see an option to add Tesseract to PATH:
>Search "Edit the system environment variables"
>
>In "Advanced"->"Environment Variable"->"System Variables"->"PATH"->"(Add path to Tesseract folder)"

Verify:
        
        where tesseract

This should return the PATH of tesseract outside your root repository

## 8. Audio Input Setup

    Uses the system microphone and Whisper for transcription.

    Note: Whisper models download automatically on first use. If a microphone is unavailable, the system defaults to text input.

System Dependencies

Linux:

    sudo apt install tesseract-ocr portaudio19-dev


macOS:

    brew install tesseract portaudio

## 9. Running the System

Start the interactive demo:

    python test.py

>You can now enter text, use the microphone, upload documents, and ask for scheme recommendations.

## 10. Example Interaction

    User: I earn less than 50000

    System: Is this monthly or annual income?

    User: Annual

    System: Eligibility context added. What schemes can benefit me?

## 11. Resilience & Fallbacks 🛡️

Convolve is designed to be "gracefully degradable." If a hardware component or dependency is missing, the system keeps running:
| Feature | Dependency  | Fallback Behavior                                   |
|--------|-------------|-----------------------------------------------------|
| Text   | None        | Always active ✅                                    |
| OCR    | Tesseract   | Skips image reading, continues with text 📄         |
| Audio  | Microphone  | Switches to text-only input 🎤                      |
| Search | Qdrant      | Notifies user if DB is unreachable 🔍               |
| Qdrant | Local       | Search unavailable                                  |


Qdrant	Not running	Search unavailable
## 12. Full Capability Checklist

To run the model at full capacity:

    [ ] Python 3.10 installed

    [ ] Dependencies installed via requirements.txt

    [ ] Qdrant running (Local)

    [ ] schemes.csv present in ingestion folder

    [ ] Tesseract installed (for OCR)

    [ ] Microphone available (for Audio)


## 🧭 How to Use the System (User Interaction Guide)

Once the application starts, you will enter an **interactive command-line session**.  
The system continuously builds an eligibility profile based on your inputs.

---

## ✍️ Input Options

You can provide information in **multiple ways**:

### 1. Text Input (Default)
Type sentences describing yourself, for example:
i am a farmer
i earn less than 50000 annually
i live in uttar pradesh
i am not SC/ST


The system automatically:
- Adds **positive eligibility information**
- asks if the salary mentioned is monthly or annual
- Tracks **exclusions** (e.g., “not SC/ST”)
- Maintains session memory across inputs

---

### 2. Audio Input
You can provide spoken input using:

audio <path-to-audio-file>

or use push-to-talk mode:
    
    push
    press enter to start recording 
    press enter to stop recording


Your speech is transcribed and treated exactly like text input.

---

### 3. Upload Documents 
You may upload supporting documents:

    upload pdf <path-to-pdf>
    upload image <path-to-image>


>If OCR is available, the text is extracted and used as **additional eligibility context**.
>
>If OCR is unavailable, the system continues to function normally.

---

## 🔍 Discovering Government Schemes

After providing enough information, type **exactly**:

    what schemes can benefit me?


This command triggers:
- Semantic search over government schemes
- State-aware filtering
- Automatic exclusion of inapplicable schemes
- Ranking based on relevance to your profile

---

## 📋 Viewing Scheme Results

You will see a numbered list of schemes.

Example:

1. Feed The Seed
   Category: Agriculture,Rural & Environment
   States: Telangana

2. Integrated Horticulture Development
   Category: Social welfare & Empowerment
   States: Assam
.
.
.


---

## 📑 Scheme Interaction Menu

After selecting a scheme number, you can choose from:

1. **Who is eligible?**  
   → Shows eligibility criteria

2. **What benefits are provided?**  
   → Displays financial or service benefits

3. **How to apply?**  
   → Explains the application process

4. **What documents are required?**  
   → Lists required documents

5. **Why was this scheme shown?**  
   → Explains *why* the scheme matches your profile  
   (semantic relevance, state match, exclusions considered)

6. **Back to scheme list**

---

## Other Commands

- Clear session memory🧹:

        clear memory

- Exit the application:

        exit

---

## 🧠 Key Design Note

The system does **not** rely on hardcoded rules for caste, gender, or income.
All matching and exclusion is done using **semantic understanding** using vector database stored in **Qdrant**, making the system flexible, explainable, and robust.

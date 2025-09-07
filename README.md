# Requirements.txt
speechrecognition==3.10.0
pydub==0.25.1
openai>=1.0.0
numpy>=1.21.0
scipy>=1.7.0
librosa>=0.9.0
pyaudio>=0.2.11
ffmpeg-python>=0.2.0

# README.md

# Truth Weaver AI Detective - The Whispering Shadows Mystery

A comprehensive solution for the Innov8 3.0 hackathon challenge organized by ARIES & Eightfold AI at Rendezvous IIT Delhi.

## 🎯 Challenge Overview

The Truth Weaver is an AI system designed to:
- Convert corrupted audio testimonies to text
- Detect contradictions across multiple sessions
- Extract truth from deceptive statements
- Generate structured analysis reports

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed on system
- Audio files in supported formats (WAV, MP3, FLAC)

### Installation

1. **Clone or extract the solution**
```bash
# If from zip file, extract to desired directory
# If from git, clone the repository
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg (required for audio processing)**

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On macOS:**
```bash
brew install ffmpeg
```

**On Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add to system PATH

4. **Install PyAudio (might need system-level packages)**

**On Ubuntu/Debian:**
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

**On macOS:**
```bash
brew install portaudio
```
**On Windows**
-pip install pyaudio


## 🚀 Usage

### Basic Usage

1. **Prepare your audio files**
   - Name them sequentially (e.g., `shadow_session1.wav`, `shadow_session2.wav`)
   - Ensure they're in a supported format

2. **Run the Truth Weaver**
```bash
python truth_weaver.py
```

3. **Modify for your case**
```python
# In main() function, update:
audio_files = [
    "path/to/session1.wav",
    "path/to/session2.wav", 
    "path/to/session3.wav",
    "path/to/session4.wav",
    "path/to/session5.wav"
]
shadow_id = "your_shadow_id"
```

### Advanced Usage

Create a new file named result.py and write this code. This will give output of the JSON and txt file for the evaluation, but it will give the output on test case.

```python
from truth_weaver import TruthWeaver

# Initialize the system
truth_weaver = TruthWeaver()

# Process a case
result, transcript = truth_weaver.process_shadow_case(
    audio_files=["session1.wav", "session2.wav"],
    shadow_id="test_shadow"
)

# Save results
truth_weaver.save_results(result, transcript, "output_directory")
```

## 📁 Output Files

The system generates:

1. **`{shadow_id}_transcript.txt`** - Combined transcript of all sessions
2. **`{shadow_id}_analysis.json`** - Structured analysis in required format

### Sample JSON Output
```json
{
  "shadow_id": "phoenix_2024",
  "revealed_truth": {
    "programming_experience": "3-4 years",
    "programming_language": "python",
    "skill_mastery": "intermediate",
    "leadership_claims": "fabricated",
    "team_experience": "individual contributor",
    "skills and other keywords": ["Machine Learning"]
  },
  "deception_patterns": [
    {
      "lie_type": "experience_inflation",
      "contradictory_claims": ["6 years", "3 years"]
    }
  ]
}
```

## 🔧 Architecture

### Core Components

1. **AudioProcessor**
   - Audio enhancement and noise reduction
   - Multi-engine speech recognition
   - Confidence scoring

2. **DeceptionAnalyzer**  
   - Pattern recognition for contradictions
   - Skill and experience extraction
   - Confidence level assessment

3. **TruthWeaver**
   - Orchestrates the entire process
   - Consolidates findings across sessions
   - Generates final truth assessment

### Key Features

- **Audio Enhancement**: Noise reduction, normalization, filtering
- **Multi-Engine Recognition**: Google Speech API + Sphinx fallback
- **Pattern Detection**: Experience claims, skill mentions, emotional states
- **Contradiction Analysis**: Cross-session comparison and validation
- **Truth Extraction**: Conservative estimation from conflicting claims

## 🧠 Algorithm Details

### Step-by-Step Process

1. **Audio Preprocessing**
   - Load and enhance audio quality
   - Apply filters to reduce noise
   - Normalize volume levels

2. **Speech-to-Text Conversion**
   - Use multiple recognition engines
   - Score confidence for each result
   - Select best transcription

3. **Content Analysis**
   - Extract experience claims using regex patterns
   - Identify mentioned skills and technologies
   - Assess confidence markers and hesitation indicators

4. **Cross-Session Comparison**
   - Compare claims across all sessions
   - Identify contradictions and inconsistencies
   - Track confidence level changes

5. **Truth Synthesis**
   - Apply conservative estimation for experience
   - Resolve conflicting skill claims
   - Determine most likely authentic statements

## 🎛️ Configuration Options

### Audio Processing Settings
```python
# In AudioProcessor.__init__()
self.recognizer.energy_threshold = 300        # Adjust for noise sensitivity
self.recognizer.pause_threshold = 0.8         # Pause detection sensitivity
self.recognizer.dynamic_energy_threshold = True  # Auto-adjust to environment
```

## 🐛 Troubleshooting

### Common Issues

1. **Audio not transcribing**
   - Check if FFmpeg is properly installed
   - Verify audio file format compatibility

2. **Missing dependencies**
   - Ensure all packages in requirements.txt are installed
   - Install system-level audio libraries (portaudio, ffmpeg)

### Error Messages

- **"Audio enhancement failed"**: Check FFmpeg installation
- **"Transcription failed"**: Verify audio file accessibility and format
- **"Processing failed"**: Check file paths and permissions


## Data

- Access datasets: https://drive.google.com/drive/folders/1ADUGc0X1-WKu5HT8e0tRNcI-21h2Db9y
# 🎬 Video Speaker Mapping App

A Streamlit-based application that processes video files to generate full transcripts using Deepgram's transcription API, applies speaker detection with an external speaker identification API, and presents a speaker mapping JSON output. The application extracts audio from the video, transcribes it, and splits the transcript into manageable chunks for speaker identification. The final output is a clean speaker mapping displayed with an interactive UI.

## ✨ Features

### 🎙️ Video Transcription
- Extracts audio from videos (mp4, mov, avi, mkv) and transcribes them using Deepgram's transcription API.

### 👥 Speaker Detection
- Identifies speakers in the transcript using a speaker identification API (via OpenrouteAPI)
- Consolidates the results if multiple transcript chunks are generated.

### 🗣️ Speaker Mapping
- Extracts a JSON speaker mapping from the raw speaker identification results using regular expressions
- Displays it in an interactive format.

### 🖥️ Streamlit Interface
- Uses Streamlit tabs to separate the transcript preview, raw identification results, and final speaker mapping for an improved user experience.

## 📋 Prerequisites

- **Python 3.7+**
- **Streamlit**: To run the interactive web interface.
- **FFmpeg**: For audio extraction from video files.
- **Deepgram API Access**:
  - Set your `DEEPGRAM_API_KEY` environment variable.
- **Speaker Identification API Access**:
  - Set your `OpenrouteAPI` environment variable (or update the code to use your preferred API key).

## 🚀 Installation

### Clone the Repository:

```bash
git clone https://github.com/PlayZone30/Speaker_Identification.git
cd Speaker_Identification
```

### Create & Activate a Virtual Environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install the Required Dependencies:

```bash
pip install -r requirements.txt
```



### Install FFmpeg:

- **On Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **On macOS**: `brew install ffmpeg`
- **On Windows**: Download FFmpeg and add it to your PATH.

### Set Up Environment Variables:
Create a `.env` file in the project root (or export them in your shell) with the following variables:

```ini
DEEPGRAM_API_KEY=your_deepgram_api_key
OpenrouteAPI=your_speaker_identification_api_key
```

## 📁 Project Structure

```
video-speaker-mapping-app/
├── Video_Transcription.py       # Contains the TranscriptProcessor class for processing videos.
├── Speaker_detection.py         # Contains the SpeakerIdentifier class for identifying speakers.
├── Consolidate_Chunk.py         # Contains the Chunk class for consolidating multiple identification results.
├── app.py                       # Main Streamlit app with the UI for file uploads and output display.
├── requirements.txt             # List of Python dependencies.
├── README.md                    # This file.
└── .env                         # Environment variable file (optional).
```

## 📝 Usage

### Run the Streamlit App:

```bash
streamlit run app.py
```

### Upload Video:
Use the interactive web interface to upload your video file (supported formats: mp4, mov, avi, mkv).

### Process and View Results:

- **Transcript Tab**: View the full transcript extracted from the video.
- **Raw Speaker Identification Output Tab**: Inspect raw results from the speaker identification API.
- **Speaker Mapping Tab**: View the final JSON mapping of speakers.


## 🔧 Troubleshooting

### FFmpeg Not Found:
Make sure FFmpeg is installed and is included in your system's PATH.

### Environment Variables Issues:
Ensure that the `.env` file exists and that you have correctly set your `DEEPGRAM_API_KEY` and `OpenrouteAPI` values.

### API Errors:
Check logs in the terminal for error messages if transcription or speaker identification fails.

## 🤝 Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to your branch: `git push origin feature/my-feature`
5. Create a pull request.

## 🙏 Acknowledgments

- Thanks to Deepgram for their transcription API.
- Thanks to the maintainers of Streamlit for enabling rapid prototyping of interactive data apps.
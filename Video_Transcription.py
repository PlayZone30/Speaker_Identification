from pathlib import Path
import os
import traceback
from typing import Optional, Any, Dict, List

import ffmpeg
# Local import for Deepgram's API
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv

load_dotenv()


class TranscriptProcessor:
    """
    A class to process video transcripts by extracting audio from a video,
    transcribing it via Deepgram's API, grouping the utterances, and saving
    the transcript into a file.
    """

    def __init__(self, video_path: Path):
        self.video_path = video_path
        self.audio_path: Optional[Path] = None
        self.transcript_details: Optional[Dict[str, Any]] = None

    def extract_audio(self) -> Path:
        """
        Extracts audio from the video file using ffmpeg.
        The resulting .wav file is saved in the same directory as the video.
        """
        try:
            self.audio_path = self.video_path.parent / f"{self.video_path.stem}_audio.wav"
            (
                ffmpeg
                .input(str(self.video_path))
                .output(str(self.audio_path), acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return self.audio_path
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise ValueError(f"Failed to extract audio from {self.video_path}")

    def transcribe_audio(self) -> Optional[Dict[str, Any]]:
        """
        Transcribes the extracted .wav audio file using Deepgram's API.
        Returns a dictionary with transcript details (utterances and paragraph transcript).
        """
        api_key = os.environ.get('DEEPGRAM_API_KEY')
        if not api_key:
            raise ValueError("Please set the DEEPGRAM_API_KEY environment variable.")
        try:
            deepgram = DeepgramClient(api_key)
            if not self.audio_path:
                raise ValueError("Audio not extracted. Run extract_audio() first.")
            with open(self.audio_path, 'rb') as audio_file:
                audio_content = audio_file.read()
            payload: FileSource = {
                'buffer': audio_content,
                'mimetype': 'audio/wav'
            }
            options = PrerecordedOptions(
                model='nova-3',
                language='en',
                smart_format=True,
                punctuate=True,
                paragraphs=True,
                diarize=True,
                utterances=True,
                utt_split=0.5,
                filler_words=False,
                profanity_filter=False
            )
            response = deepgram.listen.rest.v('1').transcribe_file(payload, options)
            print("Deepgram response:", response)
            if response and hasattr(response, 'results'):
                transcript_details = {
                    'utterances': [],
                    'paragraph_transcript': ""
                }
                channel = response.results.channels[0]
                alternative = channel.alternatives[0]
                if hasattr(alternative, 'paragraphs'):
                    paragraphs_obj = alternative.paragraphs
                    if hasattr(paragraphs_obj, 'transcript'):
                        transcript_details['paragraph_transcript'] = paragraphs_obj.transcript
                if hasattr(response.results, 'utterances'):
                    transcript_details['utterances'] = response.results.utterances
                self.transcript_details = transcript_details
                return transcript_details
            else:
                print("No transcript found.")
                return None
        except Exception as e:
            print(f"Transcription error: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def seconds_to_timestamp(seconds: float) -> str:
        """
        Converts seconds into a mm:ss formatted string.
        """
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes}:{secs:02}"

    @staticmethod
    def group_utterances_with_timestamps(utterances: List) -> List[Dict[str, Any]]:
        """
        Groups consecutive utterances by the same speaker.
        Each group includes the start time (from the first utterance in that group).
        Expects each utterance as an object with attributes 'speaker', 'transcript', and 'start'.
        """
        if not utterances:
            return []
        grouped = []
        current_speaker = getattr(utterances[0], 'speaker', 'Unknown')
        current_text = [getattr(utterances[0], 'transcript', '')]
        current_timestamp = getattr(utterances[0], 'start', 0.0)
        for utterance in utterances[1:]:
            speaker = getattr(utterance, 'speaker', 'Unknown')
            text = getattr(utterance, 'transcript', '')
            if speaker == current_speaker:
                current_text.append(text)
            else:
                grouped.append({
                    "speaker": current_speaker,
                    "timestamp": TranscriptProcessor.seconds_to_timestamp(current_timestamp),
                    "text": " ".join(current_text)
                })
                current_speaker = speaker
                current_text = [text]
                current_timestamp = getattr(utterance, 'start', 0.0)
        grouped.append({
            "speaker": current_speaker,
            "timestamp": TranscriptProcessor.seconds_to_timestamp(current_timestamp),
            "text": " ".join(current_text)
        })
        return grouped

    @staticmethod
    def create_transcript_from_utterances(grouped_segments: List[Dict[str, Any]]) -> str:
        """
        Creates a formatted transcript from grouped utterances.
        Each line follows the format: "Speaker X : text"
        """
        if not grouped_segments:
            return "No transcript available."
        transcript_lines = [
            f"Speaker {seg['speaker']} : {seg['text']}"
            for seg in grouped_segments
        ]
        return "\n".join(transcript_lines)

    def save_transcript_from_utterances(self) -> Path:
        """
        Generates a transcript file from utterances (with timestamps) and saves
        it in the video's folder. The transcript file is named after the video.
        """
        if not self.transcript_details:
            raise ValueError("No transcript details available. Please run transcribe_audio() first.")
        transcript_path = self.video_path.parent / f"{self.video_path.stem}_transcript.txt"
        utterances = self.transcript_details.get('utterances', [])
        grouped_segments = TranscriptProcessor.group_utterances_with_timestamps(utterances)
        formatted_transcript = TranscriptProcessor.create_transcript_from_utterances(grouped_segments)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)
        return transcript_path

    def process_video(self) -> Optional[Path]:
        """
        Full pipeline for processing the video:
        - Extract audio
        - Transcribe audio using Deepgram
        - Save the transcript in the video folder
        - Delete the temporary audio (.wav) file

        Returns the path to the saved transcript file, or None if an error occurred.
        """
        try:
            self.extract_audio()
            self.transcribe_audio()
            transcript_file = self.save_transcript_from_utterances()
            # Remove the temporary audio file if it exists
            if self.audio_path and self.audio_path.exists():
                os.remove(self.audio_path)
                self.audio_path = None
            return transcript_file
        except Exception as e:
            print(f"Error processing video: {e}")
            traceback.print_exc()
            return None

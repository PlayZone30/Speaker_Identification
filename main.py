import os
import re
import json
import tempfile
from pathlib import Path

import streamlit as st
from Video_Transcription import TranscriptProcessor
from Speaker_detection import SpeakerIdentifier
from Consolidate_Chunk import Chunk


def chunk_text(transcript: str, max_words: int = 5000) -> list:
    """
    Splits a transcript into chunks such that:
      - Each chunk contains complete speaker utterances (lines).
      - Each chunk begins with a speaker label.

    :param transcript: The full transcript as a string.
    :param max_words: Maximum word count allowed per chunk.
    :return: A list of transcript chunks.
    """
    lines = transcript.splitlines()
    chunks = []
    current_chunk = []
    current_word_count = 0

    for line in lines:
        if not line.strip():  # Skip empty lines
            continue

        line_word_count = len(line.split())
        # When adding this line exceeds the maximum word limit, finish the chunk.
        if current_word_count + line_word_count > max_words:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_word_count = line_word_count
        else:
            current_chunk.append(line)
            current_word_count += line_word_count

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    # Ensure each chunk begins with a speaker label.
    for idx, chunk in enumerate(chunks):
        chunk_lines = chunk.splitlines()
        if chunk_lines and not chunk_lines[0].lstrip().startswith("Speaker"):
            # Find the first line that starts with "Speaker" and add it to the beginning.
            for line in chunk_lines:
                if line.lstrip().startswith("Speaker"):
                    chunk_lines.insert(0, line)
                    break
            chunks[idx] = "\n".join(chunk_lines)

    return chunks


def extract_json_mapping(final_result: str) -> dict:
    """
    Extracts a JSON string containing a speaker mapping from the given text
    using a regular expression and returns the parsed dictionary.

    :param final_result: The speaker identification results as a string.
    :return: A dictionary with the speaker mapping if found; otherwise, an empty dict.
    """
    json_string = None
    # Try to locate a markdown-formatted JSON code block.
    m = re.search(r'```json(.*?)```', final_result, re.DOTALL)
    if m:
        json_string = m.group(1).strip()
    else:
        # Fallback: search for any JSON object substring.
        m = re.search(r'\{.*\}', final_result, re.DOTALL)
        if m:
            json_string = m.group(0).strip()

    if not json_string:
        return {}

    try:
        mapping_data = json.loads(json_string)
        return mapping_data.get("speaker_mapping", {})
    except Exception as e:
        st.error(f"Error parsing JSON mapping: {e}")
        return {}


def main():
    st.title("Video Speaker Mapping App")
    st.write("Upload a video file and get the speaker mapping from the transcript.")

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file is not None:
        # Create a placeholder for processing messages
        processing_placeholder = st.empty()
        processing_placeholder.info("Processing video... This may take a few moments.")

        # Create a placeholder for chunk processing messages
        chunk_placeholder = st.empty()

        # Save the uploaded file to a temporary directory.
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Process the video to generate a transcript.
            processor = TranscriptProcessor(file_path)
            transcript_file = processor.process_video()
            if transcript_file is None:
                st.error("Video processing failed. Check logs for details.")
                return

            with open(transcript_file, "r", encoding="utf8") as f:
                full_transcript = f.read()

            # Split transcript into manageable chunks.
            transcript_chunks = chunk_text(full_transcript, max_words=4000)
            chunk_placeholder.info(
                f"Transcript divided into {len(transcript_chunks)} chunk(s). Processing chunk 1 of {len(transcript_chunks)}...")

            API_KEY = os.environ.get('OpenrouteAPI')
            if not API_KEY:
                st.error("The OpenrouteAPI key is not set. Please set your environment variable.")
                return

            identifier = SpeakerIdentifier(API_KEY)
            results = []
            for i, chunk in enumerate(transcript_chunks):
                chunk_placeholder.info(
                    f"Transcript divided into {len(transcript_chunks)} chunk(s). Processing chunk {i + 1} of {len(transcript_chunks)}...")
                result = identifier.identify_speakers(chunk)
                if result is not None:
                    results.append(result)

            final_result = "\n".join(results)

            # Consolidate results if there are multiple chunks.
            if len(transcript_chunks) > 1:
                chunk_consolidator = Chunk(API_KEY)
                final_result = chunk_consolidator.identify_speakers(final_result)

            # Clear processing messages after completion
            processing_placeholder.empty()
            chunk_placeholder.empty()

            # Create separate tabs for Transcript Preview, Raw Output, and Speaker Mapping.
            transcript_tab, raw_output_tab, mapping_tab = st.tabs(
                ["Transcript", "Raw Speaker Identification Output", "Speaker Mapping"]
            )

            with transcript_tab:
                st.success("Transcript created successfully!")
                st.write("Full Transcript:")
                # Display complete transcript in a code block for better formatting
                st.code(full_transcript, language="text")

            with raw_output_tab:
                st.write("Speaker Identification Results:")
                # Display raw results in a code block for better formatting
                st.code(final_result, language="text")

            speaker_mapping = extract_json_mapping(final_result)
            with mapping_tab:
                if speaker_mapping:
                    st.header("Speaker Mapping")
                    st.json(speaker_mapping)
                else:
                    st.error("JSON mapping not found in the speaker identification result.")

            if transcript_file and os.path.exists(transcript_file):
                try:
                    os.remove(transcript_file)
                except Exception as e:
                    st.error(f"Error removing transcript file: {e}")


if __name__ == "__main__":
    main()
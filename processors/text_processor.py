import logging
import tempfile
import subprocess
import re
import os
import time


class TextProcessor:
    """
    Processes audio to extract text using a speech-to-text model (Whisper).
    """

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes the audio from a WAV file using Whisper.

        Args:
            audio_path: Path to the audio file.

        Returns:
            The transcribed text, or an empty string on error.
        """
        try:
            # Determine the directory of the audio file for outputting the VTT
            output_dir = os.path.dirname(audio_path)
            vtt_file_path = os.path.join(output_dir, os.path.basename(audio_path).replace(".wav", ".vtt"))

            # Use the whisper command-line tool with explicit output directory.
            command = [
                "whisper",
                audio_path,
                "--model", "small",  # You can change the model size
                "--output_format", "vtt",  # output as vtt file
                "--output_dir", output_dir  # Specify the output directory
            ]
            subprocess.run(command, check=True, capture_output=True)

            # Wait a short time to ensure the file is written
            time.sleep(0.1)

            text = self._parse_vtt(vtt_file_path)
            return text

        except subprocess.CalledProcessError as e:
            logging.error(f"Error transcribing audio: {e} {e.stderr.decode()}")
            return ""
        except FileNotFoundError:
            logging.error("Whisper not found. Please install Whisper.")
            return ""
        except Exception as e:
            logging.error(f"Error processing transcription: {e}")
            return ""

    def _parse_vtt(self, vtt_file_path: str) -> str:
        """
        Parses a VTT file and extracts the text.

        Args:
            vtt_file_path: Path to the VTT file.

        Returns:
            The extracted text as a single string.
        """
        text = ""
        try:
            with open(vtt_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # The logic to extract text might need adjustments based on the VTT format.
            for line in lines:
                if not line.strip() or line.startswith("WEBVTT") or line.startswith("NOTE") or "-->" in line:
                    continue
                text += line.strip() + " "
            return text.strip()
        except Exception as e:
            logging.error(f"Error parsing VTT file: {e}")
            return ""

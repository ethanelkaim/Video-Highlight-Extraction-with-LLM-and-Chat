import subprocess
import logging
import tempfile
import os


class AudioProcessor:
    """
    Extracts audio from video files.
    """

    def extract_audio(self, video_path: str) -> str:
        """
        Extracts the audio from a video file and saves it as a WAV file.

        Args:
            video_path: Path to the video file.

        Returns:
            Path to the extracted WAV audio file, or None on error.
        """
        # Create a temporary file to store the audio, do NOT delete on close initially
        temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = temp_audio_file.name
        temp_audio_file.close()  # Close the file handle

        try:
            # Use ffmpeg to extract the audio
            command = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # WAV format
                "-ar", "16000",  # Sample rate
                audio_path,
                "-y"  # overwrite
            ]
            subprocess.run(command, check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            logging.error(f"Error extracting audio: {e}")
            # Clean up the temporary file if ffmpeg failed
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return None
        except FileNotFoundError:
            logging.error("FFmpeg not found. Please install FFmpeg.")
            return None
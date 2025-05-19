import uuid
import logging
import time
from database.database_setup import get_db_session, create_database
from database.vector_store import store_highlight
from processors.video_processor import VideoProcessor
from processors.audio_processor import AudioProcessor
from processors.text_processor import TextProcessor
from llm_module.llm_api import generate_highlight_description, get_embedding
from config import VIDEO_STORAGE_PATH
import os
from sqlalchemy.orm import Session


def process_video(video_path: str):
    """
    Processes a video to extract highlights, descriptions, and store them in the database.

    Args:
        video_path: Path to the video file.
    """
    # Initialize processors
    video_processor = VideoProcessor()
    audio_processor = AudioProcessor()
    text_processor = TextProcessor()
    session = get_db_session()  # get session

    try:
        # 1. Extract frames
        logging.info(f"Extracting frames from {video_path}...")
        frames = video_processor.extract_frames(video_path, frame_rate=0.5)  # Extract 0.5 frame per second
        if not frames:
            logging.error(f"No frames extracted from {video_path}. Skipping.")
            return

        # 2. Detect scene changes
        logging.info(f"Detecting scene changes in {video_path}...")
        scene_changes = video_processor.detect_scene_changes(frames, threshold=0.9)  # changed threshold
        logging.info(f"Scene changes detected at frames: {scene_changes}")

        # 3. Extract audio
        logging.info(f"Extracting audio from {video_path}...")
        audio_path = audio_processor.extract_audio(video_path)
        if not audio_path:
            logging.error(f"Could not extract audio from {video_path}.  Some features may be missing.")
            audio_text = ""
        else:
            # 4. Transcribe audio
            logging.info(f"Transcribing audio from {video_path}...")
            audio_text = text_processor.transcribe_audio(audio_path)
            os.remove(audio_path)  # remove the audio file AFTER transcription

        # 5. Store video metadata
        video_filename = os.path.basename(video_path)
        video_id = store_video_metadata(session, video_filename, video_path)  # store and get video ID

        # 6. Process each scene and store highlight
        logging.info("Processing scenes and storing highlights...")
        for i in range(len(scene_changes) - 1):
            start_frame_index = scene_changes[i]
            end_frame_index = scene_changes[i + 1]
            process_scene(session, video_id, frames, start_frame_index, end_frame_index, audio_text)

        # Process the last scene
        if scene_changes:
            process_scene(session, video_id, frames, scene_changes[-1], len(frames), audio_text)

        logging.info(f"Video processing complete for {video_path}.")

    except Exception as e:
        logging.error(f"Error processing video {video_path}: {e}")
    finally:
        # Clean up temporary frame files
        if 'frames' in locals():  # check if frames variable exists
            for frame_path in frames:
                try:
                    os.remove(frame_path)
                except Exception as e:
                    logging.warning(f"Could not delete temporary frame file {frame_path}: {e}")
        session.close()


def store_video_metadata(session: Session, filename: str, path: str) -> uuid.UUID:
    """Stores video metadata in the database and returns the video ID.
    Args:
        session: Database session.
        filename:  Filename of the video.
        path: Path to the video file.
    Returns:
        The UUID of the video.
    """
    from database.models import Video
    video = Video(filename=filename, path=path)
    session.add(video)
    session.commit()
    return video.id


def process_scene(session: Session, video_id: uuid.UUID, frames: list[str], start_frame_index: int,
                  end_frame_index: int, audio_text: str):
    """Processes a single scene (range of frames) and stores the highlight.

    Args:
        session:  Database session
        video_id: ID of the video.
        frames: List of frame paths.
        start_frame_index: Index of the start frame.
        end_frame_index: Index of the end frame.
        audio_text: The full transcript of the audio.
    """
    # 1. Select a representative frame (e.g., the middle frame)
    representative_frame_index = (start_frame_index + end_frame_index) // 2
    representative_frame_path = frames[representative_frame_index]

    # 2. Generate a description of the scene
    frame_description = f"Scene from frame {start_frame_index} to {end_frame_index}.  Representative frame: {representative_frame_path}. "
    # Include relevant audio text.  This is a basic approach; more sophisticated
    #  alignment of audio to video would be better.
    scene_audio_text = "Audio: " + audio_text  # Keep it simple for now.

    prompt_for_llm = f"""
    Analyze the following video scene information.
    The scene is from frame {start_frame_index} to {end_frame_index}.
    A representative visual context is described by the (unseen by you) frame located at '{representative_frame_path}'.
    The transcribed audio for this part of the video is: "{audio_text if audio_text else 'No significant audio transcribed.'}"

    Based on this information, provide a detailed description of the scene. Specifically try to:
    1.  Estimate the number of people clearly visible or strongly implied by the context (e.g., if audio indicates a conversation between two people). If you cannot determine this, say so.
    2.  Describe the primary actions or events.
    3.  List any key objects or elements in the scene.
    4.  Summarize the overall mood or atmosphere if discernible.

    If the information is insufficient for any point, please indicate that.
    """

    # 3. Generate LLM description
    llm_description = generate_highlight_description(prompt_for_llm)
    if llm_description is None or "Error generating LLM description" in llm_description or "model's response was empty" in llm_description:
        llm_description = f"Basic scene from frame {start_frame_index} to {end_frame_index}. Audio: {audio_text if audio_text else 'N/A'}. Detailed LLM analysis was not available."
        logging.warning(f"Using fallback description for scene {start_frame_index}-{end_frame_index}")

    # 4. Generate embedding for the description
    # For storing highlights, use "RETRIEVAL_DOCUMENT"
    embedding = get_embedding(llm_description, task_type="RETRIEVAL_DOCUMENT")
    if not embedding:
        logging.warning(
            f"Could not generate embedding for scene {start_frame_index}-{end_frame_index} ('{llm_description[:50]}...'). Skipping.")
        return  # Skip if embedding fails

    # 5. Store the highlight in the database
    timestamp = start_frame_index / 1  # Use frame index as a proxy for time.  Adjust as needed.
    store_highlight(session, video_id, timestamp, llm_description, embedding)
    logging.info(f"Stored highlight for scene {start_frame_index}-{end_frame_index}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    create_database()  # Ensure database is created before processing.

    # Example usage:
    video_file_path1 = "/app/data/videos/video.mp4"  # Absolute path within the container
    # video_file_path2 = "/app/data/videos/video.mp4"  # Absolute path within the container
    if not os.path.exists(video_file_path1): #or not os.path.exists(video_file_path2):
        logging.error(f"Video file not found.  Please make sure the video files are in {VIDEO_STORAGE_PATH}.")
        exit(1)
    process_video(video_file_path1)
    # process_video(video_file_path2)
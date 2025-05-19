import cv2
import logging
import tempfile
import os


class VideoProcessor:
    """
    Processes video files to extract frames and detect scene changes.
    """

    def extract_frames(self, video_path: str, frame_rate: int = 1) -> list[str]:
        """
        Extracts frames from a video at the specified frame rate.

        Args:
            video_path: Path to the video file.
            frame_rate: Number of frames to extract per second.

        Returns:
            A list of paths to the extracted frame images, or an empty list on error.
        """
        frames = []
        try:
            video = cv2.VideoCapture(video_path)
            if not video.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")

            fps = video.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                logging.error(f"Invalid FPS in video {video_path}.  Cannot extract frames.")
                return []
            frame_interval = int(fps / frame_rate)  # Calculate frame interval

            count = 0
            frame_number = 0
            while True:
                ret, frame = video.read()
                if not ret:
                    break  # End of video

                if frame_number % frame_interval == 0:
                    # Create a temporary file to store the frame
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                        frame_path = temp_frame_file.name
                        cv2.imwrite(frame_path, frame)  # Save frame as JPEG
                        frames.append(frame_path)
                    count += 1
                frame_number += 1
            video.release()
            return frames
        except Exception as e:
            logging.error(f"Error extracting frames from {video_path}: {e}")
            return []

    def detect_scene_changes(self, frames: list[str], threshold: int = 30) -> list[int]:
        """
        Detects scene changes in a list of frames using histogram comparison.

        Args:
            frames: List of paths to frame images.
            threshold: Threshold for histogram difference (higher = less sensitive).

        Returns:
            A list of frame indices where scene changes occur.
        """
        if not frames:
            return []

        scene_changes = [0]  # The first frame is always the start of a scene
        prev_hist = None
        for i, frame_path in enumerate(frames[1:]):
            img = cv2.imread(frame_path)
            if img is None:
                logging.warning(f"Could not read frame {frame_path}. Skipping.")
                continue
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            if prev_hist is not None:
                diff = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_CORREL)
                if diff < threshold:  # Changed to less than threshold
                    scene_changes.append(i + 1)  # +1 because we started from frames[1:]
            prev_hist = hist
        return scene_changes

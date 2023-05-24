from scenedetect import SceneManager, ContentDetector
import time


class SceneChangeDetector:
    """
    Class for detecting scene changes in a video stream.

    Attributes:
        scene_manager (SceneManager): Scene detection manager.
        frame_timestamps (dict): Mapping of frame numbers to timestamps and frames.
        detected_frames (dict): Mapping of detected scene change frame numbers to frames and elapsed time.
        content_threshold (int): Content threshold value for scene change detection.
    """

    def __init__(self, frame_timestamps, detected_frames, content_threshold):
        """
        Initializes the SceneChangeDetector.

        Args:
            frame_timestamps (dict): Mapping of frame numbers to timestamps and frames.
            detected_frames (dict): Mapping of detected scene change frame numbers to frames and elapsed time.
            content_threshold (int): Content threshold value for scene change detection.
        """
        self.scene_manager = SceneManager()
        self.scene_manager.add_detector(ContentDetector(threshold=content_threshold, min_scene_len=20))
        self.frame_timestamps = frame_timestamps
        self.detected_frames = detected_frames

    def scene_change_callback(self, frame, frame_num):
        """
        Callback function for scene change detection.

        Args:
            frame_num (int): Frame number associated with the scene change.
            frame: Frame associated with the scene change.
        """
        frame_time, frame_data = self.frame_timestamps[frame_num]
        elapsed_time = time.time() - frame_time

        self.detected_frames[frame_num] = (frame, elapsed_time)

    def process_frame(self, frame_num, frame):
        """
        Processes a frame for scene change detection.

        Args:
            frame_num (int): Frame number.
            frame: Frame to process.
        """
        self.scene_manager._process_frame(frame_num=frame_num, frame_im=frame,
                                         callback=self.scene_change_callback)

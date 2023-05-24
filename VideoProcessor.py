import cv2
import os
import threading
import queue

from BlurDetector import BlurDetector
from SceneChangeDetector import SceneChangeDetector
from FrameReader import FrameReader


class VideoProcessor:
    """
    Class for processing a video by detecting scene changes and blur frames.

    Attributes:
        video_source (str): Path to the video file.
        save_scene_changes (bool): Flag indicating whether to save the detected scene changes.
        save_blur_frames (bool): Flag indicating whether to save frames below the blur threshold.
        blur_threshold (float): Blur threshold value.
        content_threshold (int): Content threshold value for scene change detection.
        frame_queue (Queue): Queue for storing video frames.
        frame_timestamps (dict): Mapping of frame numbers to timestamps.
        blur_map (dict): Mapping of frame numbers to blur values.
        detected_frames (dict): Mapping of frame numbers to (frame, elapsed_time) tuples for detected scenes.
        scene_detector (SceneChangeDetector): SceneChangeDetector instance for scene change detection.
        frame_reader (FrameReader): FrameReader instance for reading video frames.
        blur_detector (BlurDetector): BlurDetector instance for blur detection.
    """

    def __init__(self, video_source, blur_threshold, content_threshold, save_scene_changes=False, save_blur_frames=False):
        """
        Initializes the VideoProcessor instance.

        Args:
            video_source (str): Path to the video file.
            blur_threshold (float): Blur threshold value.
            content_threshold (int): Content threshold value for scene change detection.
            save_scene_changes (bool): Flag indicating whether to save the detected scene changes.
            save_blur_frames (bool): Flag indicating whether to save frames above the blur threshold.
        """
        self.video_source = video_source
        self.save_scene_changes = save_scene_changes
        self.save_blur_frames = save_blur_frames
        self.blur_threshold = blur_threshold
        self.content_threshold = content_threshold

        self.frame_queue = queue.Queue()
        self.frame_timestamps = {}
        self.blur_map = {}
        self.detected_frames = {}

        self.scene_detector = SceneChangeDetector(
            frame_timestamps=self.frame_timestamps,
            detected_frames=self.detected_frames,
            content_threshold=self.content_threshold
        )
        self.frame_reader = FrameReader(
            video_source=self.video_source,
            frame_queue=self.frame_queue,
            frame_timestamps=self.frame_timestamps,
        )
        self.blur_detector = BlurDetector(blur_map=self.blur_map)

    def process_video(self):
        """
        Processes the video by reading frames, detecting scene changes, and blur frames.
        """
        frame_reader_thread = threading.Thread(target=self.frame_reader.start_reading)
        frame_reader_thread.start()

        current_frame_count = 0
        while current_frame_count < 500:
            if self.frame_queue.qsize() == 0:
                continue
            frame_info = self.frame_queue.get()
            if frame_info is None:
                break

            frame_num, frame = frame_info

            # Create separate threads for concurrent processing of frames by the BlurDetector and SceneChangeDetector
            blur_thread = threading.Thread(target=self.blur_detector.calculate_blur, args=(frame_num, frame))
            scene_thread = threading.Thread(target=self.scene_detector.process_frame, args=(frame_num, frame))

            scene_thread.start()
            blur_thread.start()

            blur_thread.join()
            scene_thread.join()

            current_frame_count = frame_num

        frame_reader_thread.join()

        if self.save_scene_changes:
            self.save_detected_frames()

        if self.save_blur_frames:
            self.save_blur_threshold_frames()

    def save_detected_frames(self):
        """
        Saves the detected scene change frames to the output directory.
        """
        output_dir = "scene_changes"
        os.makedirs(output_dir, exist_ok=True)

        for frame_num in self.detected_frames.keys():
            frame, elapsed_time = self.detected_frames[frame_num]

            print("Scene change detected:")
            print("  Frame Num: ", frame_num)
            print("  Blur Value: ", self.blur_map[frame_num])
            print("  Time Elapsed since start (in seconds): ", elapsed_time)
            output_path = os.path.join(output_dir, f"frame_{frame_num}.jpg")
            cv2.imwrite(output_path, frame)

    def save_blur_threshold_frames(self):
        """
        Saves the frames above the blur threshold to the output directory.
        """
        output_dir = "no_blur_scene_changes"
        os.makedirs(output_dir, exist_ok=True)

        current_frame_count = 1
        for frame_num in sorted(self.detected_frames.keys()):
            if current_frame_count > frame_num:
                continue

            current_frame_count = frame_num
            while current_frame_count < 500 and self.blur_map[current_frame_count] < self.blur_threshold:
                current_frame_count += 1

            frame_time, frame_data = self.frame_timestamps[current_frame_count]
            output_path = os.path.join(output_dir, f"frame_{current_frame_count}.jpg")
            cv2.imwrite(output_path, frame_data)


# "videos/webcam-exact-resized.mp4"
# "videos/sample-video.mp4"
# "videos/living-room-sample-resized.mp4"
# "videos/living-room-sample-video.mp4"


# Example usage
video_processor = VideoProcessor(video_source="videos/living-room-sample-video.mp4",
                                 blur_threshold=60, content_threshold=15,
                                 save_scene_changes=True, save_blur_frames=True)
video_processor.process_video()

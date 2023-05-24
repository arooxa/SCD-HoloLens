import cv2
import time


class FrameReader:
    """
    Class for reading frames from a video source and adding them to a frame queue.

    Attributes:
        video_source (str): Path to the video file.
        frame_queue (Queue): Queue for storing video frames.
        frame_timestamps (dict): Mapping of frame numbers to timestamps and frames.
        is_running (bool): Flag indicating whether the frame reading is running.
    """

    def __init__(self, video_source, frame_queue, frame_timestamps):
        """
        Initializes the FrameReader instance.

        Args:
            video_source (str): Path to the video file.
            frame_queue (Queue): Queue for storing video frames.
            frame_timestamps (dict): Mapping of frame numbers to timestamps and frames.
        """
        self.video_source = video_source
        self.frame_queue = frame_queue
        self.frame_timestamps = frame_timestamps
        self.is_running = False

    def start_reading(self):
        """
        Starts reading frames from the video source and adding them to the frame queue.
        """
        self.is_running = True
        video_capture = cv2.VideoCapture(self.video_source)
        print("Width: " + str(video_capture.get(3)))
        print("Height: " + str(video_capture.get(3)))
        frame_count = 0
        while self.is_running and frame_count < 500:
            ret, frame = video_capture.read()
            if not ret:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_count += 1
            self.frame_timestamps[frame_count] = (time.time(), frame)
            self.frame_queue.put((frame_count, frame))

        self.frame_queue.put(None)
        video_capture.release()

    def stop_reading(self):
        """
        Stops the frame reading process.
        """
        self.is_running = False



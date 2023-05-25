import cv2


class VideoResizer:
    """
    A class for resizing a video file and saving the resized version.

    Attributes:
        video_path (str): Path to the input video file.
        output_path (str): Path to save the resized video.
        target_width (int): Target width for resizing.
        target_height (int): Target height for resizing.
        output_fps (float): Frames per second for the output video.
    """

    def __init__(self, video_path, output_path, target_width, target_height, output_fps=30.0):
        """
        Initializes the VideoResizer with the specified parameters.

        Args:
            video_path (str): Path to the input video file.
            output_path (str): Path to save the resized video.
            target_width (int): Target width for resizing.
            target_height (int): Target height for resizing.
            output_fps (float, optional): Frames per second for the output video. Default is 30.0.
        """
        self.video_path = video_path
        self.output_path = output_path
        self.target_width = target_width
        self.target_height = target_height
        self.output_fps = output_fps

    def resize_video(self):
        """
        Resizes the video file to the specified dimensions and saves the resized version.
        """
        cap = cv2.VideoCapture(self.video_path)

        # Get the original video's width, height, and frames per second
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        original_fps = cap.get(cv2.CAP_PROP_FPS)

        # Calculate the aspect ratio of the original video
        aspect_ratio = original_width / original_height

        # Calculate the resized height based on the target width and the original aspect ratio
        resized_height = int(self.target_width / aspect_ratio)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(self.output_path, fourcc, self.output_fps, (self.target_width, resized_height), True)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize the frame to the target dimensions
            rescaled_frame = cv2.resize(frame, (self.target_width, resized_height), interpolation=cv2.INTER_AREA)

            # Write the output frame to file
            writer.write(rescaled_frame)

            cv2.imshow("Output", rescaled_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        cap.release()
        writer.release()

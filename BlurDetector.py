import cv2


class BlurDetector:
    """
    A class for detecting blur in frames using the Laplacian variance.

    This class provides methods to calculate the blur value for a given frame
    and update a blur map. It also includes a helper method to compute the
    focus measure of a frame based on the variance of the Laplacian.

    Attributes:
        blur_map (dict): A dictionary to store frame blur values.
                         The dictionary is passed by reference, and the blur values
                         will be updated directly in the map.
    """

    def __init__(self, blur_map):
        """
        Initializes a BlurDetector instance.

        Args:
            blur_map (dict): A dictionary to store frame blur values.
                             The dictionary is passed by reference, and the blur values
                             will be updated directly in the map.
        """
        self.blur_map = blur_map

    def calculate_blur(self, frame_num, frame):
        """
        Calculates the blur value for a given frame and updates the blur map.

        Args:
            frame_num: The frame_num corresponding to the frame.
            frame: The input frame to calculate the blur for.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fm = self.compute_focus_measure(gray)
        self.blur_map[frame_num] = fm

    def compute_focus_measure(self, frame):
        """
        Compute the Laplacian of the image and then return the variance of the Laplacian for a given frame.

        Args:
            frame: The input frame to compute the focus measure for.

        Returns:
            float: The focus measure of the input frame.
        """
        return cv2.Laplacian(frame, cv2.CV_64F).var()

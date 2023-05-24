import cv2
from scenedetect import VideoStreamCv2, SceneManager, ContentDetector, AdaptiveDetector
from scenedetect.backends import VideoCaptureAdapter
import threading
import time
from functools import partial
import os

"""
This code will use CameraStream.py and try to integrate blur detection to select the best key frame
"""


def display_stream(cam):
    fps = 0
    frame_count = 0
    start_time = time.time()
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow(f"Stream 0", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_count += 1
        if frame_count % 30 == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            fps = 30 / elapsed_time
            start_time = end_time
            print(f"FPS: {fps:.2f}")

    cam.release()
    cv2.destroyAllWindows()


def process_stream(cam):
    video = VideoCaptureAdapter(cam)
    print("scene detection started")
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    # scene_manager.add_detector(AdaptiveDetector())
    start_time = cv2.getTickCount() / cv2.getTickFrequency()
    frame_timestamps = {}  # Mapping of frame numbers to timestamps

    output_folder = "frames"
    os.makedirs(output_folder, exist_ok=True)

    def scene_change_callback(frame, cut_frame_num):
        frame_time, frame_data = frame_timestamps[cut_frame_num]
        elapsed_time = time.time() - frame_time

        print("Scene change detected:")
        # print("  Frame: ", frame)
        # print("  Frame Time (in seconds): ", frame_time)
        print("  FPS: ", fps)
        print("  Frame Num: ", cut_frame_num)
        print("  Time Elapsed since start (in seconds): ", elapsed_time)

        # Save the frame to the output folder
        output_path = os.path.join(output_folder, f"frame_{cut_frame_num}.jpg")
        cv2.imwrite(output_path, frame_data)

    # Calculate the approximate frame rate manually
    fps = 0

    # Pass the callback function with arguments using functools.partial
    partial_callback = partial(scene_change_callback)
    partial_callback.scene_manager = scene_manager
    partial_callback.start_time = start_time
    partial_callback.fps = fps

    # scene_manager.detect_scenes(video=video, callback=partial_callback)
    frame_count = 0
    start_time = time.time()
    while True:
        ret, curr_frame = cam.read()
        if not ret:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_count += 1
        frame_timestamps[frame_count] = (time.time(), curr_frame)
        if frame_count % 30 == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            fps = 30 / elapsed_time
            start_time = end_time
        scene_manager._process_frame(frame_num=frame_count, frame_im=curr_frame, callback=partial_callback)

    cv2.destroyAllWindows()
    cam.release()


def calculate_frame_rate(cam):
    start_time = time.time()
    frame_count = 0
    while True:
        ret, _ = cam.read()
        if not ret:
            break
        frame_count += 1
        if time.time() - start_time >= 1:
            fps = frame_count / (time.time() - start_time)
            return fps


camera0 = cv2.VideoCapture(0)
camera1 = cv2.VideoCapture("videos/bedroom-sample-video.mp4")
camera2 = cv2.VideoCapture("videos/bedroom-sample-video.mp4")
# Start the first video stream in a separate thread (display stream in a popup window)
# thread1 = threading.Thread(target=display_stream, args=(camera1,))
# thread1.start()

# Start the second video stream in a separate thread (process stream)
thread2 = threading.Thread(target=process_stream, args=(camera2,))
thread2.start()


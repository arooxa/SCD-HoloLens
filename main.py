import cv2

from BlurDetector import BlurDetector
from SceneChangeDetector import SceneChangeDetector
from FrameReader import FrameReader
import queue
import threading
import os
import time


# "webcam-exact-resized.mp4"
# "videos/sample-video.mp4"

frame_queue = queue.Queue()
frame_timestamps = {}
frame_sizes = {}
blur_map = {}
detected_list = []

# Create the SceneChangeDetector instance and start the detection process
scene_detector = SceneChangeDetector(frame_timestamps=frame_timestamps, blur_map=blur_map, detected_list=detected_list)
# Create a frame reader and start reading frames in a separate thread
frame_reader = FrameReader(video_source=0, frame_queue=frame_queue, frame_timestamps=frame_timestamps, frame_sizes=frame_sizes)
blur_detector = BlurDetector(blur_map=blur_map)


frame_reader_thread = threading.Thread(target=frame_reader.start_reading)
frame_reader_thread.start()

current_frame_count = 0
while current_frame_count < 500:
    if frame_queue.qsize() == 0:
        continue
    frame_info = frame_queue.get()
    if frame_info is None:
        break

    frame_num, frame = frame_info

    # Create separate threads for concurrent processing of frames by the BlurDetector and SceneChangeDetector
    blur_thread = threading.Thread(target=blur_detector.calculate_blur, args=(frame_num, frame))
    scene_thread = threading.Thread(target=scene_detector.process_frame, args=(frame_num, frame))

    scene_thread.start()
    blur_thread.start()

    blur_thread.join()
    scene_thread.join()

    current_frame_count = frame_num


# Wait for the frame reader thread to finish
frame_reader_thread.join()
# print(frame_queue.qsize())
# print(frame_sizes)
current_frame_count = 1
for x in detected_list:
    if current_frame_count > x:
        print("Frame detected too close")
        continue

    current_frame_count = x
    while current_frame_count < 500 and blur_map[current_frame_count] < 35:
        current_frame_count += 1

    if current_frame_count >= 500:
        break
    frame_time, frame_data = frame_timestamps[current_frame_count]
    print("Original Frame Num: ", x)
    print("Next Best Non-Blur Frame Num: ", current_frame_count)
    output_path = os.path.join("frames2", f"frame_{current_frame_count}.jpg")
    cv2.imwrite(output_path, frame_data)

blur_threshold_pass_count = 0
for x in blur_map.keys():
    if blur_map[x] > 35:
        blur_threshold_pass_count += 1

ftime, f = frame_timestamps[1]
ftime2, f2 = frame_timestamps[500]
print("Total Time: " + str(ftime2 - ftime))
print("Total Non-Blur Images: " + str(blur_threshold_pass_count))
print("Finished Processing")



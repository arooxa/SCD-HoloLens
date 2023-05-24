import cv2


cap = cv2.VideoCapture("living-room-sample-video.mp4")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter('living-room-sample-resized.mp4',
                             fourcc, 30.0,
                             (640, 640), True)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    rescaled_frame = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_AREA)

    # write the output frame to file
    writer.write(rescaled_frame)

    cv2.imshow("Output", rescaled_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


cv2.destroyAllWindows()
cap.release()
writer.release()

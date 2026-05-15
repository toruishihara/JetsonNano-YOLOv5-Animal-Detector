import cv2
import torch

model = torch.hub.load(
    '/home/toru/yolov5',
    'yolov5n',
    source='local'
)

pipeline = (
    "nvarguscamerasrc sensor-mode=2 ! "
    "video/x-raw(memory:NVMM), width=320, height=240, framerate=15/1 ! "
    "nvvidconv ! "
    "video/x-raw, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, size=320)

    # Draw boxes and labels onto image
    results.render()

    # Get rendered image
    img = results.ims[0]

    # Show window
    cv2.imshow("YOLOv5", img)

    # Still print labels to console
    for *box, conf, cls in results.xyxy[0]:
        print(model.names[int(cls)], float(conf))

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#while True:
#    ret, frame = cap.read()
#
#    if not ret:
#        break
#
#    #results = model(frame)
#    results = model(frame, size=320)
#
#    for *box, conf, cls in results.xyxy[0]:
#        print(model.names[int(cls)], float(conf))


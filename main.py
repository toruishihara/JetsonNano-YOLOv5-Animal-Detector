import os
import cv2
import torch
from datetime import datetime
import subprocess
import time

LORA_LAST_SENT = 0
LORA_COOLDOWN_SECONDS = 60

def send_lora_alert(message):
    global LORA_LAST_SENT

    now = time.time()
    if now - LORA_LAST_SENT < LORA_COOLDOWN_SECONDS:
        return

    cmd = [
        "/home/toru/meshtastic_env/bin/meshtastic",
        "--port", "/dev/ttyACM0",
        "--sendtext", message
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=20
        )

        print("Meshtastic stdout:", result.stdout)
        print("Meshtastic stderr:", result.stderr)

        if result.returncode == 0:
            LORA_LAST_SENT = now
        else:
            print("Meshtastic send failed")

    except Exception as e:
        print("Meshtastic error:", e)


ignore_classes = {"car", "truck", "bus"}

os.makedirs("frames", exist_ok=True)

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

cnt = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    results = model(frame, size=320)

    save_frame = False

    for *box, conf, cls in results.xyxy[0]:
        class_name = model.names[int(cls)]
        confidence = float(conf)

        if class_name in ignore_classes:
            continue

        print(class_name, confidence)
        if confidence > 0.5:
            send_lora_alert(class_name)

        if confidence > 0.3:
            save_frame = True

    if save_frame:
        if cnt % 5 == 0:
            timestamp = datetime.now().strftime("%m%d_%H%M%S_%f")
            filename = f"frames/event_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print("saved:", filename)

        cnt += 1

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()




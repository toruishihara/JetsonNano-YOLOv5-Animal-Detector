import os
import cv2
import torch
from datetime import datetime
import subprocess
import time
import shutil

SAVE_CNT = 5000
LORA_LAST_SENT = 0
LORA_COOLDOWN_SECONDS = 60
USB_SAVE_DIR = "/mnt/kioxia"
USB_SAVE_DIR2 = "/mnt/kioxia1"
LOCAL_SAVE_DIR = "frames"
IGNORE_CLASSES = {"car", "truck", "bus", "person", "umbrella"}
LOCAL_LOG_FILE = "/tmp/main.log"

def copy_main_log_to_usb():
    usb_dirs = [
        USB_SAVE_DIR,
        USB_SAVE_DIR2,
    ]
    if not os.path.isfile(LOCAL_LOG_FILE):
        print("ERROR: local main.log does not exist:", LOCAL_LOG_FILE)
        return False

    for usb_dir in usb_dirs:
        if not usb_dir:
            continue
        if not os.path.isdir(usb_dir):
            print("USB dir not found:", usb_dir)
            continue

        dest_log_file = os.path.join(usb_dir, "main.log")

        try:
            shutil.copy2(LOCAL_LOG_FILE, dest_log_file)
            print("Copied main.log to:", dest_log_file)
            return True
        except Exception as e:
            pass

    print("ERROR: failed to copy main.log to both USB_SAVE_DIR and USB_SAVE_DIR2")
    return False

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

#main
os.makedirs("frames", exist_ok=True)

model = torch.hub.load(
    '/home/toru/yolov5',
    'yolov5n',
    source='local'
)

pipeline = (
    "nvarguscamerasrc sensor-mode=2 ! "
    "video/x-raw(memory:NVMM), width=320, height=240, framerate=15/1 ! "
    "nvvidconv flip-method=2 ! "
    "video/x-raw, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

cnt = 0
start_lap = time.perf_counter()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    results = model(frame, size=320)

    save_frame = False
    if cnt % SAVE_CNT == 0:
        save_frame = True

    for *box, conf, cls in results.xyxy[0]:
        class_name = model.names[int(cls)]
        confidence = float(conf)

        if class_name in IGNORE_CLASSES:
            continue

        print(class_name, confidence)
        if confidence > 0.5:
            send_lora_alert(class_name)

        if confidence > 0.4:
            save_frame = True

    if save_frame:
        results.render()
        img = results.imgs[0]

        now = datetime.now()
        ts = now.strftime("%m%d_%H%M%S") + f"_{now.microsecond // 10000}"

        save_dir1 = f"{USB_SAVE_DIR}/frames"
        save_dir2 = f"{USB_SAVE_DIR2}/frames"
        local_dir = f"{LOCAL_SAVE_DIR}/frames"

        # Choose save directory
        if os.path.isdir(save_dir1):
            save_dir = save_dir1
        elif os.path.isdir(save_dir2):
            save_dir = save_dir2
        else:
            save_dir = local_dir
            os.makedirs(save_dir, exist_ok=True)

        filename = f"{save_dir}/frame_{ts}.jpg"
        ok = cv2.imwrite(filename, img)

        if ok:
            print("saved:", filename)
        else:
            print("ERROR: failed to save:", filename)
            send_lora_alert(f"failed to save:{filename}")

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # End of loop
    cnt += 1
    if cnt % SAVE_CNT == 0:
        now = time.perf_counter()
        diff = now - start_lap

        ts = datetime.now().strftime("%H%M%S")
        fps = SAVE_CNT/diff
        print("ts=", ts, " cnt=", cnt, " fps=", fps, flush=True) 
        copy_main_log_to_usb()
        send_lora_alert(f"{ts} fps={fps}")
        start_lap = now

cap.release()

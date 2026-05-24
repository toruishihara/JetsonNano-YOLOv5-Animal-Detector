import os
import cv2
import torch
from datetime import datetime
import subprocess
import time
import shutil

SAVE_CNT = 1000
LORA_LAST_SENT = 0
LORA_COOLDOWN_SECONDS = 60
USB_SAVE_DIR = "/mnt/kioxia"
TMP_SAVE_DIR = "/mnt/night"
LOCAL_SAVE_DIR = "frames"
IGNORE_CLASSES = {"car", "truck", "bus", "person", "umbrella"}
LOCAL_LOG_FILE = "/tmp/main.log"

kioxia_exist = False
tmp_exist = False
def check_dir():
    global kioxia_exist
    global tmp_exist

    kioxia_exist = False
    tmp_exist = False

    if os.path.isdir(f"{USB_SAVE_DIR}/frames"):
        kioxia_exist = True
        print("Kioxia SDCard exist")
    if os.path.isdir(f"{TMP_SAVE_DIR}/frames"):
        tmp_exist = True
        print("tmp SDCard exist")

def copy_main_log_to_usb():
    dest_log_file = os.path.join(f"{USB_SAVE_DIR}", "main.log")

    try:
        shutil.copy2(LOCAL_LOG_FILE, dest_log_file)
        print("Copied main.log to:", dest_log_file)
        return True
    except Exception as e:
        pass

    return False


def unmount_sdcard():
    print("unmount")
    if not os.path.ismount(TMP_SAVE_DIR):
        print("Already unmounted:", TMP_SAVE_DIR)
        return True

    try:
        subprocess.run(
            ["sync"],
            check=True
        )

        subprocess.run(
            ["sudo", "umount", TMP_SAVE_DIR],
            check=True
        )

        print("Unmounted safely:", TMP_SAVE_DIR)
        return True

    except subprocess.CalledProcessError as e:
        print("Unmount failed:", e)
        return False


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
    # take a frame from camera
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    results = model(frame, size=320)

    save_frame = False
    if cnt % SAVE_CNT == 0:
        save_frame = True
        check_dir()

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
        save_dir = f"{USB_SAVE_DIR}/frames"
        filename = f"{save_dir}/frame_{ts}.jpg"
        ok = cv2.imwrite(filename, img)
        if ok:
            print("saved:", filename)
        else:
            print("ERROR: failed to save:", filename)
            # send_lora_alert(f"failed to save:{filename}")

        print("tmp_exist:", tmp_exist)
        if tmp_exist:
            tmp_dir = f"{TMP_SAVE_DIR}/frames"
            filename = f"{tmp_dir}/frame_{ts}.jpg"
            ok = cv2.imwrite(filename, img)
            if ok:
                print("saved:", filename)
            else:
                print("ERROR: failed to save:", filename)

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
        # send_lora_alert(f"{ts} fps={fps}")
        if tmp_exist:
            unmount_sdcard()

        start_lap = now

cap.release()

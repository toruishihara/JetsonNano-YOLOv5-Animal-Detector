import os
import cv2
import torch
from datetime import datetime
import subprocess
import time
import shutil
import requests
import Jetson.GPIO as GPIO

SAVE_CNT = 10000
REPORT_CNT = 50000
LORA_LAST_SENT = 0
LORA_COOLDOWN_SECONDS = 60
USB_SAVE_DIR = "/mnt/kioxia"
TMP_SAVE_DIR = "/mnt/night"
LOCAL_SAVE_DIR = "frames"
IGNORE_CLASSES = {"car", "truck", "bus", "person", "umbrella", "bed"}
LOCAL_LOG_FILE = "/tmp/main.log"

FIREBASE_URL = "https://wild-animal-detection-a6fb5-default-rtdb.asia-southeast1.firebasedatabase.app"
DEVICE_TOKEN = "f6837415369be1230d48726db857dc9bbf4fac01c8052124d2863ddb0bda7e56"
FIREBASE_LAST_SENT = 0
FIREBASE_COOLDOWN_SECONDS = 60

kioxia_exist = False
tmp_exist = False

RELAY1 = 29
RELAY2 = 31

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


def send_alert(message):
    global FIREBASE_LAST_SENT
    now_sec = time.time()
    if now_sec - FIREBASE_LAST_SENT < FIREBASE_COOLDOWN_SECONDS:
        print("Firebase skipped by cooldown")
        return False
    data = {
        "message": message,
        "time": datetime.now().isoformat(),
        "device": "jetson-nano",
        "deviceToken": DEVICE_TOKEN
    }
    try:
        r = requests.post(
            FIREBASE_URL + "/alerts.json",
            json=data,
            timeout=15
        )
        print("Firebase:", r.status_code, r.text)
        if r.status_code == 200:
            FIREBASE_LAST_SENT = now_sec
            return True
        return False
    except Exception as e:
        print("Firebase error:", e)
        return False


def every_hour_check():
    global GPIO
    now = datetime.now()
    print("hour changed:", now)
    if now.hour % 2 == 0:
        GPIO.output(RELAY1, GPIO.HIGH)   # relay 1 ON
    else:
        GPIO.output(RELAY1, GPIO.HIGH)   # relay 1 ON


#main
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY1, GPIO.OUT, initial=GPIO.HIGH) # relay 1 always ON
GPIO.setup(RELAY2, GPIO.OUT, initial=GPIO.LOW)

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
last_checked_hour = None

while True:
    now = datetime.now()
    # call a func once every hour
    if now.minute == 00 and last_checked_hour != now.hour:
        every_hour_check()
        last_checked_hour = now.hour

    # take a frame from camera
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    results = model(frame, size=320)

    save_frame = False

    if cnt % SAVE_CNT == 0 or cnt == 1000:
        save_frame = True
        check_dir()

    for *box, conf, cls in results.xyxy[0]:
        class_name = model.names[int(cls)]
        confidence = float(conf)

        if class_name in IGNORE_CLASSES:
            continue

        print(class_name, confidence)
        if confidence > 0.5:
            send_alert(class_name)

        if confidence > 0.4:
            save_frame = True

    if save_frame:
        results.render()
        img = results.imgs[0]
        ts = now.strftime("%m%d_%H%M%S") + f"_{now.microsecond // 10000}"
        save_dir = f"{USB_SAVE_DIR}/frames"
        filename = f"{save_dir}/frame_{ts}.jpg"
        ok = cv2.imwrite(filename, img)
        if ok:
            print("saved:", filename)
        else:
            print("ERROR: failed to save:", filename)
            send_alert(f"failed to save:{filename}")

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
    if cnt % REPORT_CNT == 0:
        now = time.perf_counter()
        diff = now - start_lap
        fps = REPORT_CNT/diff
        print("ts={ts} cnt={cnt} fps={fps:.2f}", flush=True) 
        send_alert(f"{ts} fps={fps:.2f}")
        start_lap = now

    if cnt % SAVE_CNT == 0:
        now = time.perf_counter()
        ts = datetime.now().strftime("%H%M%S")
        copy_main_log_to_usb()
        if tmp_exist:
            unmount_sdcard()

cap.release()
GPIO.cleanup()

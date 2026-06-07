from ultralytics import YOLO
import subprocess
import numpy as np
import cv2
import time
from pathlib import Path
from notify import send_push_with_cooldown
from blink import start_gpio_blink


# -----------------------------
# Settings
# -----------------------------
MODEL_PATH = "yolo11n.pt"

CAMERA_SENSOR_ID = 0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 360
CAMERA_FPS = 15

YOLO_IMGSZ = 320
CONF_THRES = 0.50
ANIMAL_THRES = 0.20

SAVE_DIR = Path("/usb/frames")

# Ignore these classes even if YOLO detects them
IGNORE_LIST = {
    "person",
    "car",
    "truck",
    "bus",
    "motorcycle",
    "bicycle",
}

ANIMAL_LIST = {
    "dog",
    "cat",
    "bear",
    "cow",
    "horse",
    "sheep",
    "bird",
}

# Save cooldown seconds.
# This prevents saving too many almost-same frames.
SAVE_COOLDOWN_SEC = 3.0


def build_gstreamer_command(width, height, fps):
    return [
        "gst-launch-1.0",
        "-q",
        "nvarguscamerasrc",
        f"sensor-id={CAMERA_SENSOR_ID}",
        "!",
        f"video/x-raw(memory:NVMM),width=1920,height=1080,framerate={fps}/1",
        "!",
        "nvvidconv",
        "!",
        f"video/x-raw,width={width},height={height},format=BGRx",
        "!",
        "videoconvert",
        "!",
        "video/x-raw,format=BGR",
        "!",
        "fdsink",
        "fd=1",
    ]


def main():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading model:", MODEL_PATH)
    model = YOLO(MODEL_PATH)

    names = model.names
    print("Model classes loaded:", len(names))
    print("Ignore list:", IGNORE_LIST)
    print("Save dir:", SAVE_DIR)

    frame_size = CAMERA_WIDTH * CAMERA_HEIGHT * 3

    gst_cmd = build_gstreamer_command(CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS)

    print("Starting GStreamer pipeline:")
    print(" ".join(gst_cmd))

    proc = subprocess.Popen(
        gst_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=frame_size * 4,
    )

    frame_count = 0
    saved_count = 0
    last_save_time = 0.0
    start_time = time.time()

    try:
        while True:
            raw = proc.stdout.read(frame_size)

            if len(raw) != frame_size:
                print("Could not read full frame.")
                print("Read bytes:", len(raw), "expected:", frame_size)
                break

            frame_count += 1

            frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                (CAMERA_HEIGHT, CAMERA_WIDTH, 3)
            )

            results = model(
                frame,
                imgsz=YOLO_IMGSZ,
                conf=CONF_THRES,
                verbose=False,
                device=0,
            )

            result = results[0]

            detected_items = []
            animal_detected_items = []

            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = names[cls_id]
                    
                    # 1. Animal priority check
                    # Animals can pass with lower confidence, e.g. 0.30
                    if class_name in ANIMAL_LIST:
                        if conf >= ANIMAL_CONF:
                            animal_detected_items.append((class_name, conf))
                            detected_items.append((class_name, conf))
                        continue

                    if conf < CONF_THRES:
                        continue

                    if class_name in IGNORE_LIST:
                        continue

                    detected_items.append((class_name, conf))

            now = time.time()

            if detected_items and (now - last_save_time) >= SAVE_COOLDOWN_SEC:
                annotated = result.plot()

                elapsed = now - start_time
                fps_now = frame_count / elapsed if elapsed > 0 else 0.0

                label_text = "Detected: " + ", ".join(
                    [f"{name} {conf:.2f}" for name, conf in detected_items]
                )

                start_gpio_blink()
                send_push_with_cooldown(
                    "Object",
                    label_text,
                    cooldown_sec=60
                )

                cv2.putText(
                    annotated,
                    f"FPS: {fps_now:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    annotated,
                    label_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                ts = now.strftime("%m%d_%H%M%S") + f"_{now.microsecond // 10000}"
                filename = SAVE_DIR / f"frame_{ts}.jpg"

                ok = cv2.imwrite(str(filename), annotated)

                if ok:
                    saved_count += 1
                    last_save_time = now
                    print("Saved:", filename, detected_items)
                else:
                    print("ERROR: failed to save:", filename)

            if frame_count % 100 == 0:
                elapsed = now - start_time
                fps_now = frame_count / elapsed if elapsed > 0 else 0.0
                print(
                    f"frames={frame_count}, saved={saved_count}, fps={fps_now:.1f}",
                    flush=True,
                )

    except KeyboardInterrupt:
        print("Ctrl+C received. Stopping...")

    finally:
        print("Stopping GStreamer...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

        print("Final frames:", frame_count)
        print("Final saved:", saved_count)


if __name__ == "__main__":
    main()

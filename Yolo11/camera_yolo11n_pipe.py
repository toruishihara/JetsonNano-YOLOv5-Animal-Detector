from ultralytics import YOLO
import subprocess
import numpy as np
import cv2
import time
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--output", default="camera_result.mp4")
    parser.add_argument("--no-display", action="store_true")
    args = parser.parse_args()

    print("Loading model:", args.model)
    model = YOLO(args.model)

    width = args.width
    height = args.height
    frame_size = width * height * 3

    gst_cmd = [
        "gst-launch-1.0",
        "-q",
        "nvarguscamerasrc",
        "sensor-id=0",
        "!",
        "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1",
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

    print("Starting GStreamer pipeline:")
    print(" ".join(gst_cmd))

    proc = subprocess.Popen(
        gst_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=frame_size * 4,
    )

    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.output, fourcc, 20.0, (width, height))
        print("Saving video to:", args.output)

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            raw = proc.stdout.read(frame_size)

            if len(raw) != frame_size:
                print("Could not read full frame.")
                print("Read bytes:", len(raw), "expected:", frame_size)
                break

            frame = np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 3))

            results = model(
                frame,
                imgsz=args.imgsz,
                conf=args.conf,
                verbose=False,
                device=0,
            )

            annotated = results[0].plot()

            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0

            cv2.putText(
                annotated,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
            )

            if writer is not None:
                writer.write(annotated)

            if not args.no_display:
                cv2.imshow("YOLO11n IMX219", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        print("Stopping...")
        if writer is not None:
            writer.release()
        proc.terminate()
        if not args.no_display:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

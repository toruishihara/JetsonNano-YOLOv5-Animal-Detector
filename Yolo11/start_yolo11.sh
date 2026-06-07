#!/bin/bash
set -e

docker rm -f yolo11n-detector 2>/dev/null || true

docker run \
  --name yolo11n-detector \
  --runtime nvidia \
  --network host \
  --privileged \
  -v /tmp/argus_socket:/tmp/argus_socket \
  -v /home/toru/yolo_test:/workspace/yolo_test \
  -v /mnt/usbmem0:/usb \
  -w /workspace/yolo_test/JetsonNano-YOLOv5-Animal-Detector/Yolo11 \
  yolo11n-my \
  bash -lc 'python3 -u main.py 2>&1 | tee -a /usb/main.log'

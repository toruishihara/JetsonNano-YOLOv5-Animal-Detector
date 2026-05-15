import sys
import platform
import subprocess

print("Python:", sys.version)
print("Platform:", platform.platform())
print("Machine:", platform.machine())

print("\n--- Python packages ---")

import numpy
print("numpy:", numpy.__version__)

import cv2
print("cv2:", cv2.__version__)

import torch
print("torch:", torch.__version__)
print("torch.cuda.is_available:", torch.cuda.is_available())
print("torch.version.cuda:", torch.version.cuda)

if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))
    print("CUDA current device:", torch.cuda.current_device())

try:
    print("cuDNN version:", torch.backends.cudnn.version())
    print("cuDNN enabled:", torch.backends.cudnn.enabled)
except Exception as e:
    print("cuDNN check error:", e)

import torchvision
print("torchvision:", torchvision.__version__)
print("torchvision path:", torchvision.__file__)

print("\n--- OpenCV build info ---")
print("GStreamer support:")
print("GStreamer" in cv2.getBuildInformation())

print("\n--- System commands ---")

def run(cmd):
    try:
        print(f"\n$ {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
    except Exception as e:
        print("error:", e)

run(["nvcc", "--version"])
run(["nvidia-smi"])
run(["gst-launch-1.0", "--version"])
run(["git", "--version"])


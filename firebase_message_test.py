import requests
import time
from datetime import datetime, timezone

FIREBASE_URL = "https://wild-animal-detection-a6fb5-default-rtdb.asia-southeast1.firebasedatabase.app"
DEVICE_TOKEN = "f6837415369be1230d48726db857dc9bbf4fac01c8052124d2863ddb0bda7e56"

data = {
    "message": "Test from Jetson Nano firebase_message_test.py",
    "time": datetime.now(timezone.utc).isoformat(),
    "device": "jetson-nano",
    "deviceToken": DEVICE_TOKEN
}

url = FIREBASE_URL + "/alerts.json"

try:
    r = requests.post(url, json=data, timeout=15)
    print("status:", r.status_code)
    print("response:", r.text)

    if r.status_code == 200:
        print("SUCCESS: message sent to Firebase")
    else:
        print("FAILED: Firebase rejected the request")

except Exception as e:
    print("ERROR:", e)


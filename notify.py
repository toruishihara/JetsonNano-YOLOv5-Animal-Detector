# notify.py
import json
import time
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SERVICE_ACCOUNT = "/home/toru/wild-animal-detection-a6fb5-firebase-adminsdk-fbsvc-8ec0758f8e.json"
PROJECT_ID = "wild-animal-detection-a6fb5"

FCM_TOKEN = "d9BgbfF80kyhmjABifIY91:APA91bFHQUtsW_20fgA-RaTylCL_7wBJ8kO8FtKgAy5wsmO9MeWGpX-jk0ZPwVj1FDXSrPB7Di-S-6JW--b2Im6vYUnwL17yNR3swNL2YSUZ9cZJzb-9gPM"

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

_last_push_time = 0
_access_token = None
_token_expiry_time = 0


def get_access_token():
    global _access_token, _token_expiry_time

    now = time.time()

    # Reuse token for about 50 minutes
    if _access_token and now < _token_expiry_time:
        return _access_token

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT,
        scopes=SCOPES
    )

    creds.refresh(Request())

    _access_token = creds.token
    _token_expiry_time = now + 50 * 60

    return _access_token


def send_push(title, body, data=None):
    if data is None:
        data = {}

    access_token = get_access_token()

    url = "https://fcm.googleapis.com/v1/projects/{}/messages:send".format(PROJECT_ID)

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=UTF-8",
    }

    # FCM data values must be strings
    string_data = {}
    for k, v in data.items():
        string_data[str(k)] = str(v)

    payload = {
        "message": {
            "token": FCM_TOKEN,
            "notification": {
                "title": title,
                "body": body
            },
            "data": string_data
        }
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        print("FCM status:", resp.status_code, flush=True)
        print("FCM response:", resp.text, flush=True)

        return resp.status_code == 200

    except Exception as e:
        print("FCM send error:", e, flush=True)
        return False


def send_push_with_cooldown(title, body, data=None, cooldown_sec=60):
    global _last_push_time

    now = time.time()

    if now - _last_push_time < cooldown_sec:
        print("FCM skipped by cooldown", flush=True)
        return False

    ok = send_push(title, body, data)

    if ok:
        _last_push_time = now

    return ok

if __name__ == "__main__":
    send_push("Animal Detector", "Test push from notify.py", {
        "type": "test",
        "source": "jetson"
    })

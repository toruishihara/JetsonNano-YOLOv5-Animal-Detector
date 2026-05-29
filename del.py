import requests

FIREBASE_DB_URL = "https://wild-animal-detection-a6fb5-default-rtdb.asia-southeast1.firebasedatabase.app"

url = f"https://wild-animal-detection-a6fb5-default-rtdb.asia-southeast1.firebasedatabase.app/alerts.json"

response = requests.delete(url)

print("status:", response.status_code)
print("response:", response.text)

if response.status_code == 200:
    print("SUCCESS: all alerts deleted")
else:
    print("FAILED")


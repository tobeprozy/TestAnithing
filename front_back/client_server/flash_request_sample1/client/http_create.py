import requests
import json

url = "http://172.25.4.156:5000/create"

#payload = json.dumps({"video_pt": 'rtsp://172.25.4.45:8554/mystream'})
payload = json.dumps({"img_path": 'yuv420.jpg'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)

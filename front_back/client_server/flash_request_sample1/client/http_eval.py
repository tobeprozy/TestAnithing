import requests
import json

url = "http://172.25.4.156:5000/eval"

#payload = json.dumps({"video_pt": 'rtsp://172.25.4.45:8554/mystream'})
payload = json.dumps({"eval":'done'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
response_text = response.text
response_data = json.loads(response_text)

print(response_data)
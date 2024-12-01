import requests
import json
import os
import base64
import re

url = "http://172.25.4.156:5000/result"

payload = json.dumps({})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
results = response.json()

save_dir = './results/'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for result in results:
    
    img_name = result.get('frame_id')
    jpg_base64 = result.get('jpg_base64')
    if img_name and jpg_base64:
        image_data = base64.b64decode(jpg_base64)
        save_path = os.path.join(save_dir, f'{img_name}.jpg')
        with open(save_path, 'wb') as f:
            f.write(image_data)

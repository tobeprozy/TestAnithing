import os
import time
from datetime import datetime

log_file = os.path.join(os.environ['LOG_DIR'], 'app.log')

while True:
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} 你好\n")
    time.sleep(1)
    
# sudo systemctl daemon-reload
# sudo systemctl start hello.service 
# sudo systemctl status hello.service
# sudo systemctl stop hello.service 
#!/usr/bin/env python3
import json
import os
import sys
import time

from datetime import datetime

from pathlib import Path

# python3-websocket on debian, python-websocket-client on Arch
from websocket import (
    create_connection,
)

# we want 1 second of video for 12h (8h-20h)
# this means 12 hours should be 30 frames
# meaning one picture every 24 minutes
START_AFTER_H = 8
STOP_AFTER_H = 20
INTERVAL_S = ((STOP_AFTER_H - START_AFTER_H) * 60 / 30) * 60

with open("config.json", "r") as f:
    ha_config = json.load(f)

HA_HOST = ha_config["host"]
HA_CAM_ENTITY = ha_config["camera_entity"]
HA_TOKEN = ha_config["token"]


class HaClient:
    def __init__(self):
        pass

    def connect(self):
        self.ws = create_connection(f"ws://{HA_HOST}/api/websocket")
        if self.receive()["type"] == "auth_required":
            auth = {"type": "auth", "access_token": HA_TOKEN}
            r = self.send(auth)
            if r["type"] != "auth_ok":
                print("Authentication failed")
                sys.exit()

    def send(self, dict_obj):
        self.ws.send(json.dumps(dict_obj))
        return self.receive()

    def receive(self):
        return json.loads(self.ws.recv())

    def get_hls_url(self):
        service_call = {
            "type": "camera/stream",
            "id": 41,
            "entity_id": HA_CAM_ENTITY,
        }
        hls_url = self.send(service_call)["result"]["url"]
        return f"http://{HA_HOST}{hls_url}"

    def close(self):
        self.ws.close()


c = HaClient()

CMD_PATTERN = "./ffmpeg -hide_banner -loglevel error -i {hls_url} -frames:v 1 {path}"

pictures_path = Path("timelapse")
pictures_path.mkdir(exist_ok=True)


def take_picture():
    c.connect()
    hls_url = c.get_hls_url()
    c.close()
    timestr = time.strftime("%Y%m%d-%H%M%S")
    picture_path = pictures_path / f"{timestr}.jpg"
    cmd = CMD_PATTERN.format(hls_url=hls_url, path=picture_path)
    print(cmd)
    os.system(cmd)


print('Starting up')
while True:
    now_hour = datetime.now().hour
    if now_hour >= START_AFTER_H and now_hour < STOP_AFTER_H:
        take_picture()
    else:
        print(f"Current hour {now_hour} not > {START_AFTER_H}h or < {STOP_AFTER_H}, skipping")

    print(f"Sleeping {INTERVAL_S} seconds")
    time.sleep(INTERVAL_S)

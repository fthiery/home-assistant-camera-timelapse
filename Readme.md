# Overview

Work around stupid network cameras that reject you when more than one client tries to use it.

## Install

Install `python3-websocket` on debian, `python-websocket-client` on Arch

Install ffmpeg static build from https://johnvansickle.com/ffmpeg/ (arm64 for Freebox Delta)

## Configure

Edit `HA_HOST`, `HA_CAM_ENTITY`, `HA_TOKEN`

## Systemd unit file

```
# /etc/systemd/system/timelapse.service
[Unit]
Description=Timelapse service
After=syslog.target network.target

[Service]
WorkingDirectory=/home/ha/timelapse
Type=exec
ExecStart=/usr/bin/python3 -u /home/ha/timelapse/timelapse.py

# Restart script if stopped
Restart=always
# Wait 10m before restart
RestartSec=30m

[Install]
WantedBy=multi-user.target
```

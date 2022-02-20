#!/bin/bash
groupmod -o -g "$PGID" user
usermod -o -u "$PUID" user
chown user:user /usr/src/app/app
python -u ./main.py

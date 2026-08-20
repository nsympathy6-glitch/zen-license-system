#!/bin/bash
pip3 install -r requirements.txt
nohup python3 -m server.main > server.log 2>&1 &
nohup python3 -m bot.main > bot.log 2>&1 &
echo "Server and bot started!"

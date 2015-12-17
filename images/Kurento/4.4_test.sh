#!/bin/bash

set -e

curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: $IP:8888" -H "Origin: $IP" http://$IP:8888/kurento | grep -q "Server: WebSocket++"

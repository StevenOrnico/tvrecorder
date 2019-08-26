#!/bin/bash

find /opt/iptv-recording/channels -type f -name "*.ts" -cmin +5 -exec sem -j 2 /opt/iptv-recording/encode_and_move.sh "'{}'" \;

sem --wait

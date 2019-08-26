#!/bin/bash

cd /dev/dvb/adapter0
ln -s demux0 demux1
ln -s dvr0 dvr1
ln -s net0 net1

cd /dev/dvb/adapter1
ln -s demux0 demux1
ln -s dvr0 dvr1
ln -s net0 net1

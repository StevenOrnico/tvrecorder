#!/bin/bash

SRC_ADDR=$1
DEST_DIR=$3
EXTENSION=$2

STREAM_ADDRESS="udp://$SRC_ADDR"

mkdir -p $DEST_DIR

ffmpeg \
	-i $STREAM_ADDRESS	\
	-f stream_segment	\
	-segment_atclocktime 1	\
	-segment_time 3600	\
	-map 0:v:0		\
	-map 0:a:0		\
	-c:v copy		\
	-c:a copy		\
	-strftime 1		\
	"$DEST_DIR/%Y%m%d-%H%M%S.$EXTENSION"

#	-map 0:s:0?		\
#	-c:s copy		\
read

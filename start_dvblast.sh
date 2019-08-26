#!/bin/bash

TMUX_NAME="dvblast"

function tmux_dvblast {
	echo "dvblast $@"
	tmux new-window dvblast $@ -t $TMUX_NAME
}

tmux new -s $TMUX_NAME -d

tmux_dvblast -f 11010000 -s 30000000 -v 13 -a 0 -n 1 -c 11010V.config	# DISH, SABCn
tmux_dvblast -f 11130000 -s 30000000 -v 13 -a 1 -n 1 -c 11130V.config	# ETV SS3 SS10

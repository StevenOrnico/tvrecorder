#!/bin/bash

source channel_exports
TMUX_NAME="recordings"
DEST_DIR="channels"

function record_channel_in_tmux {
	ADDR=$1
	NAME=$3
	EXT=$2
	echo -e "$ADDR\t$NAME"
	tmux new-window -n $NAME ./record_channel.sh $ADDR $EXT "./$DEST_DIR/$NAME" -t $TMUX_NAME
}

mkdir -p $DEST_DIR &> /dev/null
tmux new -s $TMUX_NAME -d &> /dev/null

# 06:00.0
 record_channel_in_tmux ${DISH[@]}
 record_channel_in_tmux ${MINDS[@]}
record_channel_in_tmux ${SABC1[@]}
record_channel_in_tmux ${SABC2[@]}
record_channel_in_tmux ${SABC3[@]}
record_channel_in_tmux ${SABCN[@]}

# 06:00.1
record_channel_in_tmux ${SS3[@]}
record_channel_in_tmux ${SS10A[@]}
record_channel_in_tmux ${MSTAR[@]}
record_channel_in_tmux ${MACTION[@]}
record_channel_in_tmux ${ETV[@]}
record_channel_in_tmux ${DMX80S[@]}

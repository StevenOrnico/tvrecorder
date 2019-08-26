file=$1
file=${file/\.\//}
file_realpath=$(realpath $file)
filename=$(basename $file)
file_mp4=${file/ts/mp4}
file_mp4_dirname=$(dirname $file_mp4)
file_mp4_realpath=$(realpath $file_mp4)

/usr/local/bin/ffmpeg		\
	-y			\
	-hwaccel cuvid		\
	-c:v mpeg2_cuvid	\
	-i "$file_realpath"	\
	-c:v h264_nvenc		\
	-c:a aac		\
	-b:a 128k		\
	-ac 2			\
	"$file_mp4_realpath"

#	-preset fast		\

if [ $? -eq 0 ]; then
	dest_dir="/mnt/nas-tv/$file_mp4_dirname/${filename:0:4}/${filename:4:2}/${filename:6:2}"
	mkdir -p $dest_dir
	mv -v $file_mp4_realpath $dest_dir && rm -v $file_realpath
fi

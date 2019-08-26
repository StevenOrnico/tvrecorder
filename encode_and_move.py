#!/usr/bin/python3

from sys import argv
from pathlib import Path
from subprocess import run, PIPE
from re import match
from shutil import copy2
from json import loads
from enum import Enum
from time import sleep


class GPU:
    def __init__(self, index, uuid, name):
        self.index = int(index)
        self.uuid = uuid
        self.name = name

    def __repr__(self):
        return f"<GPU(index={self.index}, name={self.name}, uuid={self.uuid})>"

    @staticmethod
    def nvidia_smi(params, fieldnames):
        nvidia = run([
            "nvidia-smi",
            *params,
            "--format=csv,noheader"
        ], stdout=PIPE, stderr=PIPE)

        # nvidia.check_returncode()

        if nvidia.stdout:
            return [
                dict(zip(fieldnames, n.split(",")))
                for n in nvidia.stdout.decode().splitlines()
            ]
        return None

    @classmethod
    def list(cls):
        cards = cls.nvidia_smi(
            ["--query-gpu=index,uuid,name"],
            ["index", "uuid", "name"])

        if cards:
            return [cls(**card) for card in cards]
        return None
        

    def pids(self):
        pids = self.nvidia_smi(
            ["-i", self.uuid, "--query-compute-apps=pid"],
            ["pid"])

        if pids:
            return [pid["pid"] for pid in pids]

    def busy(self):
        return len(self.pids()) == 2

    def wait(self, sleep_duration=2):
        while self.busy():
            sleep(sleep_duration)


class CodecType(Enum):
    VIDEO = "video"
    AUDIO = "audio"


class Stream:
    def __init__(self, json_stream):
        self.index = json_stream["index"]
        self.codec_name = json_stream["codec_name"]
        self.codec_long_name = json_stream["codec_long_name"]
        self.codec_type = CodecType(json_stream["codec_type"])
        self.duration = float(json_stream["duration"])
        
        # Audio only
        self.sample_rate = int(json_stream["sample_rate"]) if "sample_rate" in json_stream else 0
        self.channels = int(json_stream["channels"]) if "channels" in json_stream else 0


class CodecInformation:
    def __init__(self, source: Path):
        probe = run([
            "/usr/local/bin/ffprobe",
            "-v", "fatal",
            "-print_format", "json",
            "-show_streams",
            str(source)
        ], stdout=PIPE, stderr=PIPE)

        probe.check_returncode()

        self.streams = [Stream(stream) for stream in loads(probe.stdout)["streams"]]

    def video_codec_name_match(self, codec_name):
        return any([
            stream for stream in self.streams
            if stream.codec_type == CodecType.VIDEO and stream.codec_name == codec_name
        ])

    def audio_codec_name_match(self, codec_name):
        return any([
            stream for stream in self.streams
            if stream.codec_type == CodecType.AUDIO and stream.codec_name == codec_name
        ])


def transcode(source: Path, dest: Path, gpu: GPU):
    if not source.exists():
        print(f"Source does not exist {source}")
        return None

    if not dest.parent.exists():
        dest.parent.mkdir(parents=True)

    codec = CodecInformation(source)

    enc_gpu = ["-gpu", str(gpu.index)]
    hw_decode = ["-c:v", "mpeg2_cuvid", *enc_gpu] if codec.video_codec_name_match("mpeg2video") else []
    video_encode = ["-c:v", "copy"] if codec.video_codec_name_match("h264") else ["-c:v", "h264_nvenc", *enc_gpu]

    while True:
        gpu.wait()

        ffmpeg = run([
            "/usr/local/bin/ffmpeg",
            "-y",
            "-v", "fatal",
            "-hwaccel", "cuvid",
            *hw_decode,
            "-i", str(source),
            *video_encode,
            "-c:a", "aac",
            "-b:a", "128k",
            "-ac", "2",
            str(dest)
        ], stdout=PIPE, stderr=PIPE)

        if ffmpeg.returncode == 0:
            return ffmpeg

        print(f"Convertion failed: {source}")
        print(ffmpeg.stderr)


def main():
    if len(argv) < 3:
        print(f"Usage: {argv[0]} SOURCE DEST [--no-unlink-source] [--quiet]")
        raise SystemExit(1)

    source = Path(argv[1]).resolve()
    dest = Path(argv[2]).resolve()
    unlink_source = "--no-unlink-source" not in argv
    quiet = "--quiet" in argv

    if not quiet:
        print(f"Converting {source} => {dest}")
    gpu = GPU.list()[0]
    print(gpu)
    ffmpeg = transcode(source, dest, gpu)

    if not ffmpeg:
        print(f"Convertion failed: {source}")
        raise SystemExit(1)

    if ffmpeg and ffmpeg.returncode:
        print(f"ffmpeg failed: {ffmpeg.returncode}")
        print(ffmpeg.stdout)
        print(ffmpeg.stderr)
        raise SystemExit(1)

    if "--no-unlink-source" not in argv:
        if not quiet:
            print(f"Unlinking source {source}")
        if not source.unlink():
            if not quiet:
                print(f"Unlinking failed {source}")
            raise SystemExit(1)

#    year, month, day = match(r"(\d{4})(\d{2})(\d{2})", mp4.name).groups()
#    dest = Path("/mnt/nas-tv", mp4.parent.name, year, month, day, mp4.name)


if __name__ == "__main__":
    main()

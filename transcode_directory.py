#!/usr/bin/bash

import re
from sys import argv
from pathlib import Path
from .encode_and_move import card_busy


def argv_flag(flag):
    if flag in argv:
        return argv.pop(argv.index(flag))
    return False


def print_usage_and_exit():
    print(
        f"Usage: {argv[0]} "
        "SOURCE_DIR SOURCE_REGEX DEST_DIR DEST_FORMAT "
        "[--no-unlink-source] [--quiet] [--test-regex]")
    raise SystemExit(1)


def int_if_decimal(decimal):
    return (
        int(decimal)
        if isinstance(decimal, str) and decimal.isdecimal()
        else decimal)


def find_files(source_dir: Path, regex_match):
    for path in source_dir.iterdir():
        if path.is_dir():
            yield from files(path, regex_match)
        else:
            if regex_match.search(str(path)):
                yield path


def main():
    no_unlink = argv_flag("--no-unlink-source")
    quiet = argv_flag("--quiet")
    test = argv_flag("--test")

    if len(argv) != 5:
        print_usage_and_exit()

    source_dir = Path(argv[1]).resolve()
    source_regex = re.compile(argv[2])
    dest_dir = Path(argv[3]).resolve()

    files = find_files(source_dir, source_regex)



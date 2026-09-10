#!/usr/bin/env python3
"""
Download a YouTube video's audio and save it as an MP3.

Requires:
    pip install yt-dlp
    ffmpeg installed and on your PATH (https://ffmpeg.org/download.html)

Usage:
    python music.py "https://www.youtube.com/watch?v=XXXXXXXX"
    python music.py "https://www.youtube.com/watch?v=XXXXXXXX" -o ~/Music -q 192
"""

import argparse
import os
import shutil
import sys

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:
    sys.exit("Missing dependency. Install it with:\n    pip install yt-dlp")

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "phonemusic")


def download_mp3(url: str, out_dir: str, quality: str) -> None:
    out_dir = os.path.abspath(os.path.expanduser(out_dir))
    os.makedirs(out_dir, exist_ok=True)

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        sys.exit(
            "ffmpeg or ffprobe not found on PATH. Install FFmpeg first:\n"
            "  macOS:   brew install ffmpeg\n"
            "  Windows: winget install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg"
        )

    ydl_opts = {
        "format": "bestaudio/best",
        "paths": {"home": out_dir},
        "outtmpl": "%(title)s [%(id)s].%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"\nFinished processing: {info.get('title', 'video')}  ->  {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube audio as MP3.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT_DIR,
        help=f"Output folder (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument("-q", "--quality", default="192", choices=["64", "96", "128", "160", "192", "256", "320"], help="MP3 bitrate, e.g. 128/192/320 (default: 192)")
    args = parser.parse_args()

    try:
        download_mp3(args.url, args.output, args.quality)
    except (DownloadError, OSError) as error:
        parser.exit(1, f"Download failed: {error}\n")


if __name__ == "__main__":
    main()

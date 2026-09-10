# YouTube MP3 Downloader

Downloads a video's audio and converts it to MP3 using yt-dlp and FFmpeg.

## Setup

1. Install Python 3.10 or newer.
2. Install the Python dependencies from this folder:

   ```sh
   python -m pip install -U -r requirements.txt
   ```

3. Install [FFmpeg](https://ffmpeg.org/download.html) and ensure both `ffmpeg` and `ffprobe` are on your PATH. These are executables, not the Python package named ffmpeg.
4. For full YouTube support, install [Deno](https://deno.com/) on your PATH. Current yt-dlp uses a JavaScript runtime and its EJS package; the requirements include the default extras.

See [yt-dlp's dependency documentation](https://github.com/yt-dlp/yt-dlp#dependencies) for current requirements.

## Usage

```sh
python music.py "https://www.youtube.com/watch?v=VIDEO_ID"
python music.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "~/Music" -q 192
```

Replace VIDEO_ID with the video you want to download.

- Default destination: `Desktop/phonemusic` under your home folder.
- Use `-o` to choose a different folder, including redirected Desktop locations.
- Use `-q` for the requested MP3 bitrate: 64, 96, 128, 160, 192, 256, or 320 kbps.
- Names include the title and video ID to reduce collisions.
- Increasing bitrate cannot improve the original audio quality.
- Intended for individual video URLs; the no-playlist option selects a video when its URL also references a playlist. Avoid playlist-only URLs.
- Site changes or video availability can cause downloads to fail. Keep yt-dlp updated.

This script has not been tested with a live download.

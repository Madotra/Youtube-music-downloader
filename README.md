# YouTube Music Playlist Downloader

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Required-red)

A Python script to **download YouTube Music playlists** directly from a playlist link.

* Downloads **high-quality MP3 audio**
* Embeds **metadata** (artist, album, description)
* Embeds **high-resolution album art**
* **Skips already downloaded songs**
* Shows **progress per song** and a **final summary**
* Everything runs locally on your system, **no restrictions or accounts required**

---

## Features

* Clean filenames and folder structure
* Supports **YouTube Music playlist URLs**
* Handles songs with missing videos gracefully
* Automatically organizes songs into playlist folders

---

## Requirements

* Python 3.10+ (or compatible)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* [FFmpeg](https://ffmpeg.org/)
* [ytmusicapi](https://github.com/sigma67/ytmusicapi)

---

## Installation / Setup

### MacOS Users 🍎

1. **Install Homebrew** (if not already installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install dependencies**:

```bash
brew install ffmpeg yt-dlp
```

3. **Add yt-dlp to PATH** (if installed via pip):

```bash
nano ~/.zshrc
# Add the line at the end:
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
# Save and reload shell
source ~/.zshrc
```

4. **Install ytmusicapi**:

```bash
brew install pipx
pipx install ytmusicapi
```

---

### Windows Users 💻

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/windows/)

2. **Install dependencies via pip**:

```powershell
pip install yt-dlp ytmusicapi
```

3. **Install FFmpeg**

* Download from [FFmpeg website](https://ffmpeg.org/download.html)
* Add `bin` folder to **System PATH**

> Tip: Open PowerShell and run `ffmpeg -version` to verify installation

---

### Linux Users 🐧

1. **Install dependencies via package manager**:

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg python3-pip
pip3 install --user yt-dlp ytmusicapi
```

**Fedora/CentOS:**

```bash
sudo dnf install ffmpeg python3-pip
pip3 install --user yt-dlp ytmusicapi
```

2. **Verify installation**:

```bash
ffmpeg -version
yt-dlp --version
python3 -m pip show ytmusicapi
```

---

## Usage

1. Create project folder and Python script:

```bash
mkdir ytmusic_downloader
cd ytmusic_downloader
nano ytmusic_downloader.py
```

* Paste your final Python code into the file.
* Save (`CTRL + O`) and exit (`CTRL + X`).

2. Run the script with a playlist or album or individual track URL:

```bash
# Playlist downloader
python3 ytmusic_downloader.py "<YouTube Music Playlist URL>"

# Album downloader
python3 ytmusic_downloader.py "<YouTube Album URL>"

# Individual track downloader
python3 ytmusic_downloader.py "<YouTube Music Track URL>"

```

Example:

```bash
python3 ytmusic_downloader.py "https://music.youtube.com/playlist?list=PLQNp-BCxMEnIeSoWfDbZXzJURVnItRyBz"
```

3. Songs will be saved in `DownloadedMusic` folder, organized by playlist.

---

## Troubleshooting & Notes

* Use Python 3.10+ to avoid deprecation warnings.
* Only **playlist URLs** are supported; profile/channel URLs are not.
* Special characters in video titles are sanitized automatically.
* Already downloaded songs are skipped; deleted songs can be re-downloaded.
* Script shows progress `[current / total]` for downloading, skipped, or missing songs.
* High-resolution album art is embedded automatically.
* At the end, a summary is displayed with: total songs, downloaded this run, already in folder, skipped (no video found).

---

## License

MIT License © Sumit Kumar

---

If you have any issue or comments, please leave a comment in discussions section, I will try to resolve it as soon as possible.


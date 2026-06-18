import os
import re
import sys
from ytmusicapi import YTMusic
import subprocess


def sanitize_name(name: str) -> str:
    """Make safe folder/filename by replacing illegal characters with underscores."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def run_yt_dlp(url: str, output_folder: str):
    """Run yt-dlp to download a single track into the given folder."""
    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--add-metadata",
        "--embed-metadata",
        "--embed-thumbnail",
        "-o", os.path.join(output_folder, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(command)


def download_track(track_url: str, base_dir="DownloadedMusic"):
    """Download a single song from a YouTube or YouTube Music track URL."""
    print(f"\n=== Downloading track: {track_url} ===")
    os.makedirs(base_dir, exist_ok=True)
    run_yt_dlp(track_url, base_dir)
    print("\n✅ Track download completed!")


def download_playlist(playlist_url: str, base_dir="DownloadedMusic"):
    """Download all songs from a YouTube Music playlist with proper titles, metadata, and high-res album art."""
    print(f"\n=== Downloading playlist: {playlist_url} ===")
    ytmusic = YTMusic()
    playlist_id = playlist_url.split("list=")[-1].split("&")[0]
    playlist = ytmusic.get_playlist(playlist_id, limit=None)
    playlist_name = sanitize_name(playlist['title'])
    playlist_folder = os.path.join(base_dir, playlist_name)
    os.makedirs(playlist_folder, exist_ok=True)
    tracks = playlist['tracks']
    total_songs = len(tracks)
    downloaded_count = 0
    already_present_count = 0
    no_video_count = 0
    for idx, track in enumerate(tracks, start=1):
        song_title = sanitize_name(track['title'])
        file_path = os.path.join(playlist_folder, f"{song_title}.mp3")
        if os.path.exists(file_path):
            print(f"[{idx:3d} / {total_songs}] Already exists, skipping: {song_title}")
            already_present_count += 1
            continue
        video_id = track.get('videoId')
        if not video_id:
            print(f"[{idx:3d} / {total_songs}] ⚠️ No video found, skipping: {song_title}")
            no_video_count += 1
            continue
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"[{idx:3d} / {total_songs}] Downloading: {song_title}")
        run_yt_dlp(video_url, playlist_folder)
        downloaded_count += 1
    skipped_total = already_present_count + no_video_count
    print("\n✅ Playlist download completed!")
    print(f"Playlist: {playlist_name}")
    print(f"Total songs in playlist: {total_songs}")
    print(f"Downloaded this run: {downloaded_count}")
    print(f"Already in folder: {already_present_count}")
    print(f"Skipped (no video found): {no_video_count}")
    print(f"Total skipped: {skipped_total}")


def download_album(album_url: str, base_dir="DownloadedMusic"):
    """Download all songs from a YouTube Music album URL."""
    print(f"\n=== Downloading album: {album_url} ===")
    ytmusic = YTMusic()

    # Extract browse ID from the URL (e.g., ?list=MPREb_xxxx or /browse/MPREb_xxxx)
    browse_id = None
    if "browse/" in album_url:
        browse_id = album_url.split("browse/")[-1].split("?")[0].split("&")[0]
    elif "list=" in album_url:
        raw_id = album_url.split("list=")[-1].split("&")[0]
        # Album playlist IDs typically start with OLAK or MPREb
        if raw_id.startswith("OLAK") or raw_id.startswith("MPREb"):
            browse_id = raw_id

    if not browse_id:
        print("❌ Could not extract album ID from URL.")
        sys.exit(1)

    album = ytmusic.get_album(browse_id)
    album_title = sanitize_name(album['title'])
    artist_name = sanitize_name(album['artists'][0]['name']) if album.get('artists') else "Unknown Artist"
    album_folder = os.path.join(base_dir, artist_name, album_title)
    os.makedirs(album_folder, exist_ok=True)

    tracks = album['tracks']
    total_songs = len(tracks)
    downloaded_count = 0
    already_present_count = 0
    no_video_count = 0

    print(f"Album : {album_title}")
    print(f"Artist: {artist_name}")
    print(f"Tracks: {total_songs}\n")

    for idx, track in enumerate(tracks, start=1):
        song_title = sanitize_name(track['title'])
        file_path = os.path.join(album_folder, f"{song_title}.mp3")

        if os.path.exists(file_path):
            print(f"[{idx:3d} / {total_songs}] Already exists, skipping: {song_title}")
            already_present_count += 1
            continue

        video_id = track.get('videoId')
        if not video_id:
            print(f"[{idx:3d} / {total_songs}] ⚠️ No video found, skipping: {song_title}")
            no_video_count += 1
            continue

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"[{idx:3d} / {total_songs}] Downloading: {song_title}")
        run_yt_dlp(video_url, album_folder)
        downloaded_count += 1

    skipped_total = already_present_count + no_video_count
    print("\n✅ Album download completed!")
    print(f"Album : {album_title}")
    print(f"Total songs in album  : {total_songs}")
    print(f"Downloaded this run   : {downloaded_count}")
    print(f"Already in folder     : {already_present_count}")
    print(f"Skipped (no video)    : {no_video_count}")
    print(f"Total skipped         : {skipped_total}")


def detect_link_type(link: str) -> str:
    """Detect whether the link is a track, playlist, or album."""
    # Album browse links (music.youtube.com/browse/MPREb_...)
    if "browse/MPREb" in link or "browse/OLAK" in link:
        return "album"
    # Playlist links with album-style IDs in the list= param
    if "list=" in link:
        raw_id = link.split("list=")[-1].split("&")[0]
        if raw_id.startswith("MPREb") or raw_id.startswith("OLAK"):
            return "album"
        return "playlist"
    # Individual track links
    if "watch?v=" in link or "youtu.be/" in link:
        return "track"
    return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ytmusic_downloader.py <url>")
        print("       Supports: playlist, album, or individual track URLs")
        sys.exit(1)

    link = sys.argv[1]
    link_type = detect_link_type(link)

    if link_type == "playlist":
        download_playlist(link)
    elif link_type == "album":
        download_album(link)
    elif link_type == "track":
        download_track(link)
    else:
        print("❌ Unsupported link type. Provide a YouTube Music playlist, album, or track URL.")
        sys.exit(1)


if __name__ == "__main__":
    main()
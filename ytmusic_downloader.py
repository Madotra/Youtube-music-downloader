import os
import re
import sys
import argparse
import shutil
import subprocess
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from ytmusicapi import YTMusic
from tqdm import tqdm

def check_dependencies():
    """Check if external dependencies are installed."""
    missing = []
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    
    if missing:
        print(f"❌ Error: Missing dependencies: {', '.join(missing)}")
        print("Please install them and ensure they are in your PATH.")
        print("Install yt-dlp: pip install yt-dlp")
        print("Install ffmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

def sanitize_name(name: str) -> str:
    """Make safe folder/filename by replacing illegal characters with underscores."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def download_track(track, playlist_folder, browser=None, cookies_file=None, forced_filename=None):
    """
    Download a single track.
    Returns a status string: 'downloaded', 'exists', 'skipped', 'error'
    """
    # Use forced_filename if provided, ensuring uniqueness
    if forced_filename:
        song_title = forced_filename
    else:
        song_title = sanitize_name(track['title'])
        
    file_path = os.path.join(playlist_folder, f"{song_title}.mp3")

    # Skip if file already exists
    if os.path.exists(file_path):
        return 'exists', song_title

    # Skip if no videoId
    video_id = track.get('videoId')
    if not video_id:
        return 'skipped', song_title

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # yt-dlp command
    command_download = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--add-metadata",
        "--embed-metadata",
        "--embed-thumbnail",
        "--no-playlist", # Ensure only single video is downloaded
        "-q",            # Quiet mode to not mess up tqdm
        "--no-warnings",
        # Force the filename we calculated to avoid 'yt-dlp' deciding something different
        "-o", os.path.join(playlist_folder, f"{song_title}.%(ext)s"),
        video_url
    ]

    if cookies_file:
         command_download.insert(1, "--cookies")
         command_download.insert(2, cookies_file)
    elif browser:
        command_download.insert(1, f"--cookies-from-browser")
        command_download.insert(2, browser)

    try:
        # Capture stderr to show error details if it fails
        result = subprocess.run(
            command_download, 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE,
            text=True
        )
        return 'downloaded', song_title
    except subprocess.CalledProcessError as e:
        # Return the error message from yt-dlp (clean up newlines)
        error_msg = e.stderr.strip().split('\n')[-1] if e.stderr else "Unknown error"
        return 'error', f"{song_title} -> {error_msg}"
    except Exception as e:
        return 'error', f"{song_title} ({str(e)})"

def download_playlist(playlist_url: str, output_dir: str, max_workers: int, browser: str = None, cookies_file: str = None):
    """Download all songs from a YouTube Music playlist using a thread pool."""
    print(f"\n🔍 Fetching playlist info...")
    
    try:
        ytmusic = YTMusic()
        playlist_id = playlist_url.split("list=")[-1].split("&")[0]
        playlist = ytmusic.get_playlist(playlist_id, limit=None)
    except Exception as e:
        print(f"❌ Error fetching playlist: {e}")
        return

    playlist_name = sanitize_name(playlist['title'])
    playlist_folder = os.path.join(output_dir, playlist_name)
    os.makedirs(playlist_folder, exist_ok=True)
    
    tracks = playlist['tracks']
    total_songs = len(tracks)
    
    print(f"🎵 Playlist: {playlist_name}")
    print(f"📂 Output Folder: {playlist_folder}")
    print(f"🔢 Total Songs: {total_songs}")
    print(f"🚀 Starting download with {max_workers} threads...\n")

    print(f"🚀 Starting download with {max_workers} threads...\n")

    stats = {
        'downloaded': 0,
        'exists': 0,
        'skipped': 0,
        'error': 0
    }

    # Pre-process tracks to handle duplicates and name collisions
    unique_tasks = []
    seen_ids = set()
    filename_counter = {}

    for track in tracks:
        vid = track.get('videoId')
        # If no video ID, we can't really check duplicates, but download_track handles it.
        # We process it normally but it will likely fail/skip in download_track.
        if vid:
            if vid in seen_ids:
                continue # Skip exact duplicate song (same ID)
            seen_ids.add(vid)
        
        # Determine unique filename
        base_title = sanitize_name(track['title'])
        
        if base_title in filename_counter:
            filename_counter[base_title] += 1
            # Append counter to filename: "Song (1)"
            safe_filename = f"{base_title} ({filename_counter[base_title]})"
        else:
            filename_counter[base_title] = 0
            safe_filename = base_title
            
        unique_tasks.append((track, safe_filename))

    total_unique = len(unique_tasks)
    print(f"ℹ️  Uniques tracks: {total_unique} (removed {total_songs - total_unique} duplicates)")

    # Parallel processing with tqdm progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures
        future_to_track = {
            executor.submit(download_track, track, playlist_folder, browser, cookies_file, safe_filename): track 
            for track, safe_filename in unique_tasks
        }
        
        with tqdm(total=total_unique, unit="song", desc="Downloading") as pbar:
            for future in concurrent.futures.as_completed(future_to_track):
                status, name = future.result()
                stats[status] += 1
                
                # Update progress bar description with last action
                if status == 'error':
                    pbar.write(f"❌ Error downloading: {name}")
                
                pbar.update(1)

    print("\n✅ Download completed!")
    print(f"📥 Downloaded: {stats['downloaded']}")
    print(f"⏭️  Already exists: {stats['exists']}")
    print(f"⚠️  Skipped (no video): {stats['skipped']}")
    print(f"❌ Errors: {stats['error']}")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube Music playlists with metadata and album art.")
    parser.add_argument("url", help="YouTube Music Playlist URL")
    parser.add_argument("-o", "--output", default="DownloadedMusic", help="Output directory (default: DownloadedMusic)")
    parser.add_argument("-j", "--jobs", type=int, default=4, help="Number of parallel downloads (default: 4)")
    parser.add_argument("-b", "--browser", help="Browser to load cookies from (chrome, firefox, edge)")
    parser.add_argument("-c", "--cookies", help="Path to cookies.txt file (bypass correct browser/DPAPI issues)")
    
    args = parser.parse_args()

    check_dependencies()
    
    if "playlist?list=" not in args.url:
        print("❌ Error: URL must be a YouTube Music playlist (contains 'playlist?list=').")
        sys.exit(1)

    download_playlist(args.url, args.output, args.jobs, args.browser, args.cookies)

if __name__ == "__main__":
    main()
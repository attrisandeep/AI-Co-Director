import os
import uuid
import subprocess
import tempfile

TMP_DIR = "/tmp/multimodal_backend"
os.makedirs(TMP_DIR, exist_ok=True)

def save_upload_and_trim(file_bytes, filename, start=None, end=None):
    """
    Trim video reliably using ffmpeg subprocess.
    Handles multi-stream MP4s (5.1 audio, chapters, subtitles).
    """
    input_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}_{filename}")
    with open(input_path, "wb") as f:
        f.write(file_bytes)

    start = float(start or 0)
    end = float(end or 0)

    # Determine duration (fallback to 300s if not available)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            capture_output=True, text=True, check=True
        )
        duration = float(probe.stdout.strip())
    except Exception:
        duration = 300.0

    if end == 0 or end > duration:
        end = min(duration, 300.0)
    if end - start > 300:
        end = start + 300.0

    output_path = os.path.join(TMP_DIR, f"trimmed_{uuid.uuid4().hex}.mp4")

    # Build a clean ffmpeg command:
    # - maps only first video and first audio stream
    # - forces re-encode (avoids "At least one output file" issue)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", input_path,
        "-map", "0:v:0", "-map", "0:a:0?",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k",
        "-ac", "2",  # force stereo
        "-movflags", "+faststart",
        output_path
    ]

    try:
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed:\n{e.stderr.decode(errors='ignore')[:500]}")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("ffmpeg trimming succeeded but output file is empty.")

    return output_path, end - start

import subprocess
from pathlib import Path

def combine_audio_and_video(video_file,
                            main_audio,
                            background_audio,
                            tmp_original_video_path,
                            output_format
                            ):
    original_path = Path(tmp_original_video_path)
    output_file = original_path.with_name(f"{original_path.stem}_translated.{output_format}")
    
    command = [
        "ffmpeg",
        "-y",
        "-i", main_audio,
        "-i", background_audio,
        "-filter_complex",
        "[0:a]volume=1.2[a0];[a0][1:a]amix=inputs=2:duration=longest[aout]",
        "-i", video_file,
        "-map", "2:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "libopus",
        "-b:a", "192k",
        str(output_file)
    ]
    subprocess.run(command, check=True)
    
    return str(output_file), output_file.name
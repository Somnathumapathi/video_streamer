import boto3
from sercrets_keys import SecretKeys
from enum import Enum
import subprocess
import os

class TranscoderType(Enum):
    HLS = "HLS"
    DASH = "DASH"

transcode_cmd = {
    "HLS": lambda input_path, output_dir: [
 "ffmpeg",
            "-i",
            input_path,
            "-filter_complex",
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=640:360:flags=fast_bilinear[360p];"
            "[v2]scale=1280:720:flags=fast_bilinear[720p];"
            "[v3]scale=1920:1080:flags=fast_bilinear[1080p]",
            "-map",
            "[360p]",
            "-map",
            "[720p]",
            "-map",
            "[1080p]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            "-sc_threshold",
            "0",
            "-b:v:0",
            "1000k",
            "-b:v:1",
            "4000k",
            "-b:v:2",
            "8000k",
            "-f",
            "hls",
            "-hls_time",
            "6",
            "-hls_playlist_type",
            "vod",
            "-hls_flags",
            "independent_segments",
            "-hls_segment_type",
            "mpegts",
            "-hls_list_size",
            "0",
            "-master_pl_name",
            "master.m3u8",
            "-var_stream_map",
            "v:0 v:1 v:2",
                "-hls_segment_filename",
                f"{output_dir}/%v/segment_%03d.ts",
                f"{output_dir}/%v/playlist.m3u8",
        ],
    
    "DASH": lambda input_path, output_dir: [
            "ffmpeg",
            "-i",
            input_path,
            "-filter_complex",
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=640:360:flags=fast_bilinear[360p];"
            "[v2]scale=1280:720:flags=fast_bilinear[720p];"
            "[v3]scale=1920:1080:flags=fast_bilinear[1080p]",
            # 360p video stream
            "-map",
            "[360p]",
            "-c:v:0",
            "libx264",
            "-b:v:0",
            "1000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 720p video stream
            "-map",
            "[720p]",
            "-c:v:1",
            "libx264",
            "-b:v:1",
            "4000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 1080p video stream
            "-map",
            "[1080p]",
            "-c:v:2",
            "libx264",
            "-b:v:2",
            "8000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # Audio stream
            "-map",
            "0:a",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            # DASH specific settings
            "-use_timeline",
            "1",
            "-use_template",
            "1",
            "-window_size",
            "5",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-f",
            "dash",
            f"{output_dir}/manifest.mpd",
        ]
}


class AdaptiveBitrateTranscoder:
    def __init__(self, type: str):
        self.type = str
        # if str == "HLS":
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=SecretKeys.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=SecretKeys.AWS_SECRET_ACCESS_KEY,
            region_name=SecretKeys.AWS_REGION
        )
    def _get_content_type(self, file_path: str) -> str:
        if file_path.endswith(".m3u8"):
            return "application/vnd.apple.mpegurl"
        elif file_path.endswith(".ts"):
            return "video/MP2T"
        elif file_path.endswith(".mpd"):
            return "application/dash+xml"
        elif file_path.endswith(".m4s"):
            return "video/mp4"
        
    def download_video(self, local_path):
        self.s3_client.download_file(
            SecretKeys.AWS_S3_BUCKET,
            SecretKeys.AWS_S3_KEY,
            local_path
        )

    def transcode_video(self, input_path, output_path):
        transcode_process = subprocess.run(transcode_cmd[self.type](input_path, output_path))
        if transcode_process.returncode != 0:
            raise Exception("Transcoding failed")
        
    def upload_to_s3(self, prefix, local_dir):
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = f"{prefix}/{os.path.relpath(local_file_path, local_dir)}"
                self.s3_client.upload_file(local_file_path, SecretKeys.AWS_S3_PROCESSED_VIDEOS_BUCKET, s3_key,
                                           ExtraArgs={'ContentType': self._get_content_type(local_file_path)})
                
    def process_video(self):
        from pathlib import Path
        work_dir = Path("temp/work_space")
        work_dir.mkdir(exist_ok=True)
        input_path = work_dir / "input.mp4"
        output_path = work_dir / "output"
        output_path.mkdir(exist_ok=True)
        
        try:
            self.download_video(input_path)
            self.transcode_video(str(input_path), str(output_path))
            self.upload_to_s3(SecretKeys.AWS_S3_KEY, str(output_path))
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                for file in output_path.iterdir():
                    file.unlink()
                output_path.rmdir()
    

if __name__ == "__main__":
    VideoTranscoder = AdaptiveBitrateTranscoder(TranscoderType.HLS)
    VideoTranscoder.process_video()


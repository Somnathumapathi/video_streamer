# from boto3 import 

class Transducer:
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir

    def transcode(self):
        input_path = self.input_path
        output_dir = self.output_dir

        # Create the command to run ffmpeg

cmd = [
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
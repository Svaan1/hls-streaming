from pathlib import Path
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=[
        'settings.toml',
        '.secrets.toml',
    ],
    case_sensitive=False,
)

settings.validators.register(
    Validator('video_folder_path', must_exist=True, condition=lambda x: Path(x).exists()),
    Validator('hls_output', must_exist=True, condition=lambda x: Path(x).exists()),

    Validator('ffmpeg.binary_path', must_exist=True, condition=lambda x: Path(x).exists()),
    Validator('ffmpeg.video_bitrate', must_exist=True, is_type_of=str),
    Validator('ffmpeg.video_encoder', must_exist=True, is_type_of=str),
    Validator('ffmpeg.audio_bitrate', must_exist=True, is_type_of=str),
    Validator('ffmpeg.audio_encoder', must_exist=True, is_type_of=str),
    Validator('ffmpeg.audio_sample_rate', must_exist=True, is_type_of=str),
    Validator('ffmpeg.preset', must_exist=True, is_type_of=str),
    Validator('ffmpeg.hls_time', must_exist=True, is_type_of=str),
    Validator('ffmpeg.hls_list_size', must_exist=True, is_type_of=str),
    Validator('ffmpeg.hls_flags', must_exist=True, is_type_of=str),
)

settings.validators.validate_all()
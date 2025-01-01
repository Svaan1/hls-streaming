from typing import Any, Dict

from dynaconf import Dynaconf
from pydantic import BaseModel, FilePath


class FFmpegSettings(BaseModel):
    binary_path: FilePath
    video_bitrate: str
    video_encoder: str
    audio_bitrate: str
    audio_encoder: str
    audio_sample_rate: str
    preset: str
    hls_time: str
    hls_list_size: str
    hls_flags: str


class MetricsSettings(BaseModel):
    interval: int


class Settings(BaseModel):
    hls_output: str
    channels: Dict[str, Any]
    ffmpeg: FFmpegSettings
    metrics: MetricsSettings

    @classmethod
    def from_dynaconf(cls, dynaconf_settings: Dynaconf) -> "Settings":
        settings_dict = {
            "hls_output": dynaconf_settings.hls_output,
            "channels": dynaconf_settings.channels,
            "metrics": {"interval": dynaconf_settings.metrics.interval},
            "ffmpeg": {
                "binary_path": dynaconf_settings.ffmpeg.binary_path,
                "video_bitrate": dynaconf_settings.ffmpeg.video_bitrate,
                "video_encoder": dynaconf_settings.ffmpeg.video_encoder,
                "audio_bitrate": dynaconf_settings.ffmpeg.audio_bitrate,
                "audio_encoder": dynaconf_settings.ffmpeg.audio_encoder,
                "audio_sample_rate": dynaconf_settings.ffmpeg.audio_sample_rate,
                "preset": dynaconf_settings.ffmpeg.preset,
                "hls_time": dynaconf_settings.ffmpeg.hls_time,
                "hls_list_size": dynaconf_settings.ffmpeg.hls_list_size,
                "hls_flags": dynaconf_settings.ffmpeg.hls_flags,
            },
        }
        return cls(**settings_dict)


dynaconf_settings = Dynaconf(
    settings_files=[
        "settings.toml",
        ".secrets.toml",
    ],
    case_sensitive=False,
)

settings = Settings.from_dynaconf(dynaconf_settings)

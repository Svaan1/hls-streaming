from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

class Config(CustomBaseSettings):
    
    VIDEO_FOLDER_PATH: str

    FFMPEG_PATH: str
    FFMPEG_OUTPUT_PATH: str

    @model_validator(mode="after")
    def validate_paths(self):
        if not Path(self.VIDEO_FOLDER_PATH).exists():
            raise ValueError(f"VIDEO_FOLDER_PATH {self.VIDEO_FOLDER_PATH} does not exist")

        if not Path(self.FFMPEG_PATH).exists():
            raise ValueError(f"FFMPEG_PATH {self.FFMPEG_PATH} does not exist")

        if not Path(self.FFMPEG_OUTPUT_PATH).exists():
            raise ValueError(f"FFMPEG_OUTPUT_PATH {self.FFMPEG_OUTPUT_PATH} does not exist")

        return self


settings = Config()
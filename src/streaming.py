import asyncio
import random
from pathlib import Path

from src.config import settings
from src.logger import logger
from src.utils import get_folder_videos


class StreamingManager:
    def __init__(self, channel_name, video_folders):
        self.channel_name = channel_name
        self.output_path = Path(settings.hls_output) / self.channel_name
        self.current_process = None
        self.loop_task = None
        self.run_loop = False
        self.video_options = []

        logger.info(f"Initializing streaming manager for channel {self.channel_name}...")

        self._initialize_video_folders(video_folders)
        self._ensure_output_directory()

    # Initialization methods ==================================================

    def _initialize_video_folders(self, video_folders) -> None:
        for folder in video_folders:
            videos = get_folder_videos(folder)
            self.video_options.append(videos)

        number_of_folders = len(self.video_options)
        total_videos = sum(len(folder) for folder in self.video_options)
        logger.info(f"Found {number_of_folders} video folders with {total_videos} total videos")

    def _ensure_output_directory(self) -> None:
        self.output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using output directory: {self.output_path}")

    # Public methods =========================================================

    async def start_loop(self):
        if self.loop_task is not None:
            logger.warning("Streaming loop is already running")
            return

        logger.info("Starting streaming loop...")
        self.run_loop = True
        self.loop_task = asyncio.create_task(self._loop())
        logger.info("Streaming loop started")

    async def stop_loop(self):
        logger.info("Streaming stopping loop...")
        await self._stop_streaming()
        if self.loop_task is not None:
            self.run_loop = False
            self.loop_task.cancel()
        logger.info("Streaming loop stopped")

    # Private methods ========================================================

    async def _loop(self):
        while self.run_loop:
            if self.current_process is not None:
                await asyncio.sleep(1)
                continue

            current_video = self._get_random_video()
            await self._stream_video(current_video)
            self.current_process = None

    async def _stream_video(self, input_file):
        if self.current_process is not None:
            return

        try:
            cmd = self._build_ffmpeg_command(input_file)
            logger.info(f"Streaming video with command: {' '.join(cmd)}")

            with open(self.output_path / "ffmpeg.log", "a") as log_file:
                self.current_process = await asyncio.create_subprocess_exec(*cmd, stdout=log_file, stderr=log_file)
                await self.current_process.communicate()

            logger.info("Video stream completed")

        except Exception as e:
            logger.error(f"Error streaming video: {e}")
            await self.stop_loop()
            return

    async def _stop_streaming(self):
        if self.current_process is None:
            self._clean_files()
            return

        try:
            self.current_process.terminate()
            try:
                await asyncio.wait_for(self.current_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Process did not terminate within timeout, forcing...")
                self.current_process.kill()
                await self.current_process.wait()
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
        finally:
            self._clean_files()
            self.current_process = None

    def _get_random_video(self):
        random_folder = random.choice(self.video_options)
        return random.choice(random_folder)

    def _clean_files(self):
        logger.info("Cleaning up streaming files...")
        extensions = (".ts", ".m3u8", ".vtt")

        for file_path in self.output_path.glob("*"):
            if file_path.suffix in extensions:
                try:
                    file_path.unlink()
                except OSError as e:
                    logger.error(f"Error deleting file {file_path}: {e}")

    def _build_ffmpeg_command(self, input_file):
        return [
            settings.ffmpeg.binary_path,
            "-re",
            "-i",
            input_file,
            "-b:v",
            settings.ffmpeg.video_bitrate,
            "-c:v",
            settings.ffmpeg.video_encoder,
            "-b:a",
            settings.ffmpeg.audio_bitrate,
            "-c:a",
            settings.ffmpeg.audio_encoder,
            "-preset",
            settings.ffmpeg.preset,
            "-ar",
            settings.ffmpeg.audio_sample_rate,
            "-hls_time",
            settings.ffmpeg.hls_time,
            "-hls_list_size",
            settings.ffmpeg.hls_list_size,
            "-hls_flags",
            settings.ffmpeg.hls_flags,
            "-sn",
            str(self.output_path) + "/index.m3u8",
        ]

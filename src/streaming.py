import asyncio
import os
import random
from pathlib import Path

from src.config import settings
from src.logger import logger
from src.utils import get_folder_videos


class StreamingManager:
    def __init__(self, channel_name, video_folders):
        self.channel_name = channel_name
        self.output_path = Path(settings.hls_output) / self.channel_name

        logger.info(f"Initializing streaming manager for channel {self.channel_name}...")

        self.video_options = []

        for folder in video_folders:
            self.video_options.append(get_folder_videos(folder))

        logger.info(
            f"Found {len(self.video_options)} video folders with a total of {sum(len(folder) for folder in self.video_options)} videos."
        )

        self.current_process = None
        self.loop_task = None
        self.run_loop = False

        if not os.path.exists(self.output_path):
            logger.info(f"Creating output folder: {self.output_path}")
            os.makedirs(self.output_path)

    async def start_loop(self):
        self.run_loop = True
        self.loop_task = asyncio.create_task(self._loop())

    async def stop_loop(self):
        logger.info("Stopping loop...")
        await self._stop_streaming()
        if self.loop_task is not None:
            self.run_loop = False
            self.loop_task.cancel()

    async def _loop(self):
        while self.run_loop:
            if self.current_process is not None:
                await asyncio.sleep(1)
                continue

            if self.current_process is None:
                logger.info("Starting new video stream...")
                current_video = self.get_random_video()
                await self._stream_video(current_video)
                self.current_process = None
                logger.info("Video stream ended.")

    async def _stream_video(self, input_file):
        if self.current_process is not None:
            return

        try:
            cmd = self.get_ffmpeg_command(input_file)
            logger.info(f"Streaming video with command: {' '.join(cmd)}")

            with open(self.output_path / "ffmpeg.log", "w") as log_file:
                self.current_process = await asyncio.create_subprocess_exec(
                    *cmd, stdout=log_file, stderr=log_file
                )
                await self.current_process.communicate()

        except Exception as e:
            logger.error(f"Error streaming video: {e}")
            await self.stop_loop()
            return

    async def _stop_streaming(self):
        if self.current_process is None:
            self.clean_files()
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
            self.clean_files()
            self.current_process = None

    def get_random_video(self):
        random_folder = random.choice(self.video_options)
        return random.choice(random_folder)

    def clean_files(self):
        logger.info("Cleaning up files...")

        extensions = (".ts", ".m3u8", ".vtt")
        for file in os.listdir(self.output_path):
            if not file.endswith(extensions):
                continue

            file_path = self.output_path / file
            file_path.unlink()

    def get_ffmpeg_command(self, input_file):
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

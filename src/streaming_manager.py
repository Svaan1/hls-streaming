import asyncio

from pathlib import Path
from src.config import settings
import os

from src.utils import get_video_choices, shuffle_videos

class StreamingManager:
    def __init__(self, logger):
        self.logger = logger

        self.current_process = None
        self.loop_task = None
        self.run_loop = False

    async def start_loop(self):
        self.run_loop = True
        self.loop_task = asyncio.create_task(self._loop())

    async def stop_loop(self):
        self.logger.info("Stopping loop...")
        await self._stop_streaming()
        if self.loop_task is not None:
            self.run_loop = False
            self.loop_task.cancel()
            await self.loop_task

    async def _loop(self):
        videos = []
        shuffled_videos = []

        while self.run_loop:
            # Check if we need to check for new videos
            if not shuffled_videos:
                videos = get_video_choices(video_folder=settings.VIDEO_FOLDER_PATH)
                shuffled_videos = shuffle_videos(videos)
                self.logger.info(f"Found {len(shuffled_videos)} videos, shuffling...")

            # Check if the process is already running
            if self.current_process is not None:
                await asyncio.sleep(1)
                continue
            
            # Start a new process if there are videos to stream and no process is running
            if self.current_process is None:
                self.logger.info("Starting new video stream...")
                current_video = shuffled_videos.pop(0)
                await self._stream_video(current_video)
                self.current_process = None
                self.logger.info("Video stream ended.")

            
    async def _stream_video(self, input_file):
        # Check if a process is already running
        if self.current_process is not None:
            return

        try:
            # Define the ffmpeg command
            cmd = get_ffmpeg_command(input_file)
            self.logger.info(f"Streaming video with command: {' '.join(cmd)}")	

            # Start the process sending the output to a log file
            with open("ffmpeg.log", "w") as log_file:
                self.current_process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=log_file,
                    stderr=log_file
                )
                await self.current_process.communicate()

        except Exception as e:
            self.logger.error(f"Error streaming video: {e}")
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
                self.logger.warning("Process did not terminate within timeout, forcing...")
                self.current_process.kill()
                await self.current_process.wait()

        except Exception as e:
            self.logger.error(f"Error stopping stream: {e}")

        finally:
            self.clean_files()
            self.current_process = None
    
    def clean_files(self):
        self.logger.info("Cleaning up files...")

        extensions = ('.ts', '.m3u8', '.vtt')
        for file in os.listdir(settings.FFMPEG_OUTPUT_PATH):
            if not file.endswith(extensions):
                continue

            file_path = Path(settings.FFMPEG_OUTPUT_PATH) / file
            file_path.unlink()
        
def get_ffmpeg_command(input_file):
    return [
        settings.FFMPEG_PATH,
        '-re',
        '-i', input_file,
        '-preset', settings.PRESET,
        '-c:v', settings.VIDEO_ENCODER,
        '-c:a', settings.AUDIO_ENCODER,
        '-b:v', settings.VIDEO_BIRATE,
        '-b:a', settings.AUDIO_BIRATE,
        '-ar', settings.AUDIO_SAMPLE_RATE,
        '-hls_time', settings.HLS_TIME,
        '-hls_list_size', settings.HLS_LIST_SIZE,
        '-hls_flags', settings.HLS_FLAGS,
        f'{settings.FFMPEG_OUTPUT_PATH}/index.m3u8'
    ]



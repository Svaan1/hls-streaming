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
        self.run_loop = False
        if self.loop_task is not None:
            self.loop_task.cancel()
            await self.loop_task

    async def _loop(self):
        videos = []
        shuffled_videos = []

        while self.run_loop:
            self.logger.info("Started new loop...")

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
                self.logger.info(f"Streaming video: {current_video}")
                await self._stream_video(current_video)
                self.current_process = None
                self.logger.info("Video stream ended.")

            
    async def _stream_video(self, input_file):
        # Check if a process is already running
        if self.current_process is not None:
            return

        try:
            # Define the ffmpeg command
            cmd = [
                settings.FFMPEG_PATH,
                '-re',
                '-i', input_file,
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
                '-hls_time', '4',
                '-hls_list_size', '5',
                '-hls_flags', 'delete_segments',
                f'{settings.FFMPEG_OUTPUT_PATH}/index.m3u8'
            ]

            self.logger.info(f"Streaming video with command: {' '.join(cmd)}")	

            # Start the process sending the output to /dev/null
            self.current_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await self.current_process.wait()
        except Exception as e:
            print
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


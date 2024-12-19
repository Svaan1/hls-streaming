from threading import Lock
import asyncio
import logging

from utils import get_video_choices, shuffle_videos

# thread safe singleton, idk if i need this, here for now
# i was afraid multiple workers could mess up and create multiple ffmpeg processes
# will have to test tho
class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class StreamingManager(metaclass=SingletonMeta):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.current_process = None
        self.loop_task = None
        self.loop_running = False

    async def start_loop(self):
        self.loop_running = True
        self.loop_task = asyncio.create_task(self._loop())

    async def stop_loop(self):
        if self.loop_task is not None:
            self.loop_running = False
            self.loop_task.cancel()
            await self.loop_task

    async def _loop(self):
        videos = []

        while self.loop_running:
            if not videos:
                videos = get_video_choices(video_folder="videos")
                videos = shuffle_videos(videos)

            if self.current_process is not None:
                await asyncio.sleep(1)
                continue

            if self.current_process is None:
                current_video = videos.pop(0)
                await self._stream_video(current_video)
                await self.current_process.wait()
                self.current_process = None

            
    async def _stream_video(self, input_file):
        if self.current_process is not None:
            return

        cmd = [
            'bin/ffmpeg',
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
            'hls/index.m3u8'
        ]

        self.current_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
            )
    
    async def _stop_streaming(self):
        if self.current_process is None:
            return
        
        try:
            self.current_process.terminate()
            
            try:
                await asyncio.wait_for(self.current_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning("Process did not terminate within timeout, forcing...")
                self.current_process.kill()
                await self.current_process.wait()

        except Exception as e:  # TODO: specify exception
            self.logger.error(f"Error stopping stream: {e}")

        finally:
            self.current_process = None

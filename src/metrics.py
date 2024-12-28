import asyncio
from datetime import datetime

import psutil
from prometheus_client import Gauge, start_http_server

from src.config import settings
from src.logger import logger
from src.streaming import StreamingManager


class MetricsTracker:
    streaming_managers: list[StreamingManager]
    cpu_gauges: dict[str, Gauge]
    memory_gauges: dict[str, Gauge]
    run_loop: bool
    loop_task: asyncio.Task | None

    def __init__(self, streaming_managers):
        self.streaming_managers = streaming_managers
        self.cpu_gauges = {}
        self.memory_gauges = {}
        self.run_loop = False
        self.loop_task = None

        logger.info("Initializing metrics tracker")

        self._initialize_gauges()

    # Initialization methods ==================================================

    def _initialize_gauges(self):
        for streaming_manager in self.streaming_managers:
            self.cpu_gauges[streaming_manager.channel_name] = Gauge(
                f"{streaming_manager.channel_name}_cpu_percent",
                f"CPU usage of the channel {streaming_manager.channel_name}",
            )

            self.memory_gauges[streaming_manager.channel_name] = Gauge(
                f"{streaming_manager.channel_name}_memory_usage",
                f"Memory usage of the channel {streaming_manager.channel_name}",
            )

    # Public methods =========================================================

    async def start_loop(self):
        logger.info("Starting metrics tracker")
        try:
            start_http_server(8001)
        except Exception as e:
            logger.error("Failed to start metrics server on port 8001: " + str(e))
            return
        self.run_loop = True
        self.loop_task = asyncio.create_task(self._loop())
        logger.info("Metrics tracker started")

    async def stop_loop(self):
        logger.info("Stopping metrics tracker")
        self.run_loop = False
        if self.loop_task is not None:
            self.loop_task.cancel()
        logger.info("Metrics tracker stopped")

    # Private methods ========================================================

    async def _loop(self):
        while self.run_loop:
            try:
                await self._collect_metrics()
            except Exception as e:
                logger.error("Failed to collect metrics: " + str(e))
                return
            await asyncio.sleep(15)

    async def _collect_metrics(self):
        for streaming_manager in self.streaming_managers:
            if streaming_manager.current_process is None:
                continue

            p = psutil.Process(streaming_manager.current_process.pid)

            cpu_gauge = self.cpu_gauges[streaming_manager.channel_name]
            memory_gauge = self.memory_gauges[streaming_manager.channel_name]

            cpu_usage = p.cpu_percent(interval=1.0)
            memory_usage = p.memory_info().rss

            cpu_gauge.set(cpu_usage)
            memory_gauge.set(memory_usage)

            with open(settings.hls_output + "/" + streaming_manager.channel_name + "/metrics.log", "a") as log_file:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_file.write(f"[{timestamp}] PID: {streaming_manager.current_process.pid} CPU: {cpu_usage} Memory: {memory_usage}\n")

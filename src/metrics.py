from prometheus_client import start_http_server, Gauge
import psutil
import asyncio

from src.logger import logger

class MetricsTracker:
    def __init__(self, streaming_managers):
        self.streaming_managers = streaming_managers

        self.run_loop = False
        self.loop_task = None

        logger.info('Initializing metrics tracker')

        self.cpu_gauges = {streaming_manager.channel_name: Gauge(f'{streaming_manager.channel_name}_cpu_percent', f'CPU usage of the channel {streaming_manager.channel_name}') for streaming_manager in self.streaming_managers}
        self.memory_gauges = {streaming_manager.channel_name: Gauge(f'{streaming_manager.channel_name}_memory_usage', f'Memory usage of the channel {streaming_manager.channel_name}') for streaming_manager in self.streaming_managers}

        logger.info('Metrics tracker initialized')
            
    async def start_loop(self):
        logger.info('Starting metrics tracker')
        try:
            start_http_server(8001)
        except Exception as e:
            logger.error('Failed to start metrics server on port 8001: ' + str(e))
            return
        logger.info('Metrics tracker started')
        self.run_loop = True
        self.loop_task = asyncio.create_task(self._loop())

    async def stop_loop(self):
        self.run_loop = False
        if self.loop_task is not None:
            self.loop_task.cancel()

    async def _loop(self):
        while self.run_loop:
            try:
                await self._collect_metrics()
            except Exception as e:
                logger.error('Failed to collect metrics: ' + str(e))
                return
            await asyncio.sleep(15)

    async def _collect_metrics(self):
        for streaming_manager in self.streaming_managers:
            if streaming_manager.current_process is None:
                continue
            
            p = psutil.Process(streaming_manager.current_process.pid)

            cpu_usage = self.cpu_gauges[streaming_manager.channel_name]
            memory_usage = self.memory_gauges[streaming_manager.channel_name]
            cpu_usage.set(p.cpu_percent(interval=1.0))
            memory_usage.set(p.memory_info().rss)
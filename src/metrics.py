import asyncio
from datetime import datetime

import psutil
import requests
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
        self._initialize_grafana_dashboard()

    # Initialization methods ==================================================

    def _initialize_gauges(self):
        for streaming_manager in self.streaming_managers:
            self.cpu_gauges[streaming_manager.channel_name] = Gauge(
                name=f"{streaming_manager.channel_name}_cpu_percent",
                documentation=f"CPU usage percentage for {streaming_manager.channel_name}",
            )

            self.memory_gauges[streaming_manager.channel_name] = Gauge(
                name=f"{streaming_manager.channel_name}_memory_usage",
                documentation=f"Memory usage in bytes for {streaming_manager.channel_name}",
            )

    def _initialize_grafana_dashboard(self):
        url = "http://localhost:3000/api/dashboards/db"
        headers = {"Content-Type": "application/json"}

        payload = self._build_dashboard_payload()
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info("Grafana dashboard created successfully")
        else:
            logger.error("Failed to create Grafana dashboard")

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
            await asyncio.sleep(settings.metrics.interval)

    async def _collect_metrics(self):
        for streaming_manager in self.streaming_managers:
            if streaming_manager.current_process is None:
                continue

            try:
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

            except Exception as e:
                with open(settings.hls_output + "/" + streaming_manager.channel_name + "/metrics.log", "a") as log_file:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_file.write(f"[{timestamp}] Failed to collect metrics: {str(e)}\n")

    def _build_dashboard_payload(self):
        cpu_panels = []
        memory_panels = []

        for index, streaming_manager in enumerate(self.streaming_managers):
            cpu_title = f"{streaming_manager.channel_name.capitalize()} CPU Usage"
            cpu_expression = f"{streaming_manager.channel_name}_cpu_percent"

            memory_title = f"{streaming_manager.channel_name.capitalize()} Memory Usage"
            memory_expression = f"{streaming_manager.channel_name}_memory_usage"

            cpu_panels.append(self._build_panel_payload(cpu_title, cpu_expression, x=0, y=index * 8))
            memory_panels.append(self._build_panel_payload(memory_title, memory_expression, x=12, y=index * 8))

        return {
            "dashboard": {
                "id": None,
                "uid": "fe8mwxn1jury8d",
                "title": "Video Stream Dashboard",
                "tags": [],
                "panels": cpu_panels + memory_panels,
                "schemaVersion": 36,
                "version": 0,
            },
            "folderId": 0,
            "overwrite": True,
        }

    def _build_panel_payload(self, title, expression, x, y):
        return {
            "type": "timeseries",
            "datasource": "Prometheus",
            "title": title,
            "targets": [
                {
                    "disableTextWrap": False,
                    "editorMode": "builder",
                    "expr": expression,
                    "fullMetaSearch": False,
                    "includeNullMetadata": True,
                    "legendFormat": "__auto",
                    "range": True,
                    "refId": "A",
                    "useBackend": False,
                }
            ],
            "gridPos": {"x": x, "y": y, "h": 8, "w": 12},
        }

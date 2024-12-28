from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.metrics import MetricsTracker
from src.streaming import StreamingManager

# Start the streaming manager for each channel, then start the metrics tracker

streaming_managers: List[StreamingManager] = []

for channel, folders in settings.channels.items():
    streaming_manager = StreamingManager(channel_name=channel, video_folders=folders)
    streaming_managers.append(streaming_manager)

metrics_tracker = MetricsTracker(streaming_managers)


# Define the startup and shutdown routines


async def on_startup():
    for streaming_manager in streaming_managers:
        await streaming_manager.start_loop()
    await metrics_tracker.start_loop()


async def on_shutdown():
    for streaming_manager in streaming_managers:
        await streaming_manager.stop_loop()
    await metrics_tracker.stop_loop()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await on_startup()
        yield
    finally:
        await on_shutdown()


# Create the FastAPI app, including middleware, templates, mounted directories and routes

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/hls", StaticFiles(directory=settings.hls_output), name="hls")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_channels": [channel_name for channel_name in settings.channels],
        },
    )

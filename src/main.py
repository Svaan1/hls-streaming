from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.streaming import StreamingManager
from src.config import settings

streaming_managers = []

for channel_name in settings.channels:
    video_folders = settings.channels[channel_name]
    streaming_manager = StreamingManager(channel_name=channel_name, video_folders=video_folders)
    streaming_managers.append(streaming_manager)

@asynccontextmanager
async def lifespan(_app):
    try:
        for streaming_manager in streaming_managers:
            await streaming_manager.start_loop()
        yield
    finally:
        for streaming_manager in streaming_managers:
            await streaming_manager.stop_loop()

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
    return templates.TemplateResponse("index.html", {"request": request, "available_channels": [channel_name for channel_name in settings.channels]})
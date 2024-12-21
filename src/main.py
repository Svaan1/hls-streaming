import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.streaming_manager import StreamingManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

streaming_manager = StreamingManager(logger)

@asynccontextmanager
async def lifespan(_app):
    try:
        await streaming_manager.start_loop()
        yield
    finally:
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

app.mount("/hls", StaticFiles(directory="hls"), name="hls")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

import logging

from streaming_manager import StreamingManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

streaming_manager = StreamingManager(logger)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await streaming_manager.start_loop()
    yield
    await streaming_manager.stop_loop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/hls", StaticFiles(directory="hls"), name="hls")

@app.get("/")
async def read_root():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
import logging
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse

from backend.database import db_manager
from backend.scheduler import reminder_scheduler
from backend.api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("assistant.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Assistant Service Lifecycle...")
    await db_manager.connect()
    reminder_scheduler.start()
    await reminder_scheduler.load_and_schedule_all()
    yield
    logger.info("Shutting down Assistant Service Lifecycle...")
    reminder_scheduler.shutdown()

app = FastAPI(
    title="AI Personal Assistant Automation API",
    description="Backend service using LangChain, FastAPI, MongoDB, and APScheduler",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def read_index():
    return FileResponse("frontend/html/index.html")

app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/components", StaticFiles(directory="frontend/html/components"), name="components")

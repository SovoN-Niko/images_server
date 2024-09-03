import asyncio
import logging.config
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import db, UPLOAD_DIR
from app.loger import LOGGING_CONFIG, create_log_folder
from app.routers import image_api
from app.service.image_service import ImageService

origins = ["http://localhost:3000"]


def init_app():
    create_log_folder()
    create_image_folder()

    logging.config.dictConfig(LOGGING_CONFIG)
    botLog = logging.getLogger(__name__)

    db.init()

    app = FastAPI(title="IMAGE_SERVICE")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def starup():
        await db.create_all()
        asyncio.create_task(ImageService.apply_filter())

    @app.on_event("shutdown")
    async def shutdown():
        await db.close()

    app.include_router(image_api.router)

    return app
def create_image_folder(folder=UPLOAD_DIR):
    if not os.path.exists(folder):
        os.mkdir(folder)

app = init_app()



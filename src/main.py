import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

import asyncio

from api.views.user.router import router as auth_router
from api.views.image.router import router as image_router

from config import settings, uvicorn_config
from api.services.rabbit_utilities import RABBITMQ_PUBLISHER

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

v1 = APIRouter(prefix="/api/v1")
v1.include_router(auth_router)
v1.include_router(image_router)


app.include_router(v1)

@app.on_event("startup")
async def startup_event():
    await RABBITMQ_PUBLISHER.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await RABBITMQ_PUBLISHER.close()

async def main():
    server = uvicorn.Server(uvicorn_config)
    await asyncio.gather(
        server.serve(),
        RABBITMQ_PUBLISHER.consume_image_events(),
    )

if __name__ == "__main__":
    asyncio.run(main())
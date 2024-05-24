from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.router import api_router
from db.tortoise_config import init_db

app = FastAPI()

app.include_router(api_router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://192.168.68.129:8000",
    "http://localhost:3000",
    "http://192.168.68.129:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await init_db()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.urls.routes import router as urls_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls_router)

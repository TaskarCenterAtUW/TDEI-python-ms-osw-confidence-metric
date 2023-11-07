from typing import Union
from fastapi import FastAPI, Request, APIRouter, Depends,status
from fastapi.responses import Response
from python_ms_core import Core
from .config import Settings
from functools import lru_cache


app = FastAPI()

prefix_router = APIRouter(prefix='/health')

@lru_cache()
def get_settings():
    return Settings()

@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings))->None:
    print('\n Service has started up')

@app.get('/',status_code=status.HTTP_200_OK)
@prefix_router.get('/',status_code=status.HTTP_200_OK)
def health_check():
    return "I'm health !!"

app.include_router(prefix_router)
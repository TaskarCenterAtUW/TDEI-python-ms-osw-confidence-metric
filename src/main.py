from typing import Union
from fastapi import FastAPI, Request, APIRouter, Depends,status
from fastapi.responses import Response
from python_ms_core import Core
from .config import Settings
from functools import lru_cache
from src.service.osw_confidence_service import OSWConfidenceService
import os
import psutil


app = FastAPI()

prefix_router = APIRouter(prefix='/health')

@lru_cache()
def get_settings():
    return Settings()

@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings))->None:
    print('\n Service has started up')
    try:
        OSWConfidenceService()
    except:
        print('Killing the service')
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

@app.get('/',status_code=status.HTTP_200_OK)
@prefix_router.get('/',status_code=status.HTTP_200_OK)
def health_check():
    return "I'm health !!"

app.include_router(prefix_router)
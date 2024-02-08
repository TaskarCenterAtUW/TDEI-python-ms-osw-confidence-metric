import os
import psutil
from threading import Thread
from src.config import Settings
from functools import lru_cache
from fastapi import FastAPI, APIRouter, Depends, status
from src.service.osw_confidence_service import OSWConfidenceService

app = FastAPI()

prefix_router = APIRouter(prefix='/health')


def start_confidence_metric():
    OSWConfidenceService()


def run_in_background(target):
    thread = Thread(target=target)
    thread.start()


@lru_cache()
def get_settings():
    return Settings()


@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings)) -> None:
    print('\n Service has started up')
    try:
        run_in_background(start_confidence_metric)
    except Exception as e:
        print('Killing the service')
        print(e)
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()


@app.get('/', status_code=status.HTTP_200_OK)
@prefix_router.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return "I'm healthy !!"


app.include_router(prefix_router)

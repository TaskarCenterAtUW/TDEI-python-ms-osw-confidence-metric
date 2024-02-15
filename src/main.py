import os
import psutil
from threading import Thread
from src.config import Settings
from functools import lru_cache
from fastapi import FastAPI, APIRouter, Depends, status
from src.service.osw_confidence_service import OSWConfidenceService
from dotenv import load_dotenv
import threading
import time
from osw_confidence_metric.area_analyzer import AreaAnalyzer
from osw_confidence_metric.osm_data_handler import OSMDataHandler
import requests

load_dotenv()
app = FastAPI()

prefix_router = APIRouter(prefix='/health')


@lru_cache()
def get_settings():
    return Settings()


@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings)) -> None:
    print('\n Service has started up')
    try:
        OSWConfidenceService()
        print("Current cpu count")
        print(os.cpu_count())
    except Exception as e:
        print('Killing the service')
        print(e)
        print('QCON')
        print(os.environ.get('QUEUECONNECTION','w'))
        
        # print(os.environ)
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()


@app.get('/', status_code=status.HTTP_200_OK)
@prefix_router.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return "I'm healthy !!"

@app.get('/test-route',status_code=status.HTTP_200_OK)
@prefix_router.get('/test-route',status_code=status.HTTP_200_OK)
def test_check():
    # create a thread and start with integration
    small_tester()
    return 'Started testing'


@app.get('/test-network',status_code=status.HTTP_200_OK)
def test_network():
    response = requests.get('http://www.google.com')
    print(response)
    return 'network ready'

def small_tester():
    print('Small testser started')
    settings = Settings()
    osm_data_handler = OSMDataHandler(username=settings.username, password=settings.password)
    area_analyzer = AreaAnalyzer(osm_data_handler=osm_data_handler)
    asset_path = os.path.join(settings.get_assets_folder(),'caphill_mini.geojson')
    process_thread = threading.Thread(target=analyse_score, args=[asset_path,area_analyzer])
    process_thread.start()
    
    

def analyse_score(file_path:str, area_analyzer: AreaAnalyzer) :
    print('Analysis score started')
    start_time = time.time()
    score = area_analyzer.calculate_area_confidence_score(file_path=file_path)
    print(score)
    print("--- %s seconds ---" % (time.time() - start_time))

app.include_router(prefix_router)

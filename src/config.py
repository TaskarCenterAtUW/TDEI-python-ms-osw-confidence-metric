import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    app_name: str = 'osw-confidence-metric-service-python'
    incoming_topic_name: str = os.environ.get('CONFIDENCE_REQ_TOPIC','')
    incoming_topic_subscription: str = os.environ.get('CONFIDENCE_REQ_SUB','')
    outgoing_topic_name: str = os.environ.get('CONFIDENCE_RES_TOPIC','')
    storage_container_name: str = os.environ.get('CONTAINER_NAME','osw')
    
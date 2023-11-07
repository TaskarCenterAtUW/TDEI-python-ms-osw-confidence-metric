# Service that handles the confidence calculation
import logging
from src.config import Settings
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_request import ConfidenceRequest
import threading


logging.basicConfig()


class OSWConfidenceService:

    def __init__(self):
        core = Core()
        self.settings = Settings()
        self.incoming_topic = core.get_topic(self.settings.incoming_topic_name)
        self.outgoing_topic = core.get_topic(self.settings.outgoing_topic_name)
        self.storage_client = core.get_storage_client()
        self.subscribe()
        self.logger = logging.getLogger('OSWConfService')
        self.logger.setLevel(logging.INFO)
        
    
    def subscribe(self) -> None:
        self.incoming_topic.subscribe(self.settings.incoming_topic_subscription,self.process)

    
    def process(self, msg : QueueMessage):
        print('Confidence calculation request received')
        self.logger.info(msg)
        # Have to start with the processing of message
        try:
            confidence_request = ConfidenceRequest(**msg.data)
            # create a thread and complete the message
            process_thread = threading.Thread(target=self.calculate_confidence,args=[confidence_request])
            process_thread.start()
        except TypeError as e:
            print(' Type error occured')
            print(e)
            print(msg)
            # Need to send failure message here.
    
    def calculate_confidence(self, request:ConfidenceRequest):
        pass

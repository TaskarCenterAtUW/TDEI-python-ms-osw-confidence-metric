# Service that handles the confidence calculation
import logging
from src.config import Settings
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_request import ConfidenceRequest
from src.models.confidence_response import ConfidenceResponse
from dataclasses import asdict

import threading
import os

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
        self.logger.info('Confidence service initiated')
        self.logger.info('Downloads folder ')
        self.logger.info(self.settings.get_download_folder())
        # Make the downloads folder if it does not exist
        if not os.path.exists(self.settings.get_download_folder()):
            os.makedirs(self.settings.get_download_folder())

    def subscribe(self) -> None:
        self.incoming_topic.subscribe(self.settings.incoming_topic_subscription, self.process)

    def process(self, msg: QueueMessage):
        print('Confidence calculation request received')
        self.logger.info(msg)
        # Have to start with the processing of message
        try:
            confidence_request = ConfidenceRequest( messageType=msg.messageType, messageId=msg.messageId,data= msg.data)
            # create a thread and complete the message
            process_thread = threading.Thread(target=self.calculate_confidence, args=[confidence_request])
            process_thread.start()
        except TypeError as e:
            print(' Type error occured')
            print(e)
            print(msg)
            # Need to send failure message here.

    def calculate_confidence(self, request: ConfidenceRequest):
        # make a directory for the request
        jobId = request.data.jobId
        local_base_path = os.path.join(self.settings.get_download_folder(), jobId)
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)
        osw_file_local_path = os.path.join(local_base_path, 'osw.zip')  # Assuming zip file
        self.download_single_file(request.data.data_file, osw_file_local_path)
        meta_file_local_path = os.path.join(local_base_path, 'meta.json')  # Assuming json file
        self.download_single_file(request.data.meta_file, meta_file_local_path)
        # The meta file is at `meta_file_local_path`
        # The osw file is at `osw_file_local_path`
        # insert code for calculation here.

        # creating a dummy response now
        response = ConfidenceResponse(
            jobId=jobId,
            confidence_level='90.0',
            confidence_library_version='v1.0',
            status='finished',
            message='Processed successfully',
            success=True
        )
        self.logger.info('Sending response for confidence')
        self.send_response_message(response, request)

    # utility functions for downloading and other stuff
    def download_single_file(self, remote_url: str, local_path: str):
        self.logger.info(f'Downloading {remote_url}')
        self.logger.info(f' to  {local_path}')
        file = self.storage_client.get_file_from_url(self.settings.storage_container_name, remote_url)

        try:
            if file.file_path:
                with open(local_path, 'wb') as blob:
                    blob.write(file.get_stream())
                self.logger.info(' File downloaded ')
            else:
                self.logger.info('File path not found')
        except Exception as e:
            self.logger.error(e)

    # Sending response message
    def send_response_message(self, response: ConfidenceResponse, request: ConfidenceRequest):
        queue_message = QueueMessage.data_from({
            'messageId': request.messageId,
            'messageType': request.messageType,
            'data': asdict(response)
        })
        self.outgoing_topic.publish(queue_message)

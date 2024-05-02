# Service that handles the confidence calculation
import os
import json
import logging
import threading
import osw_confidence_metric
from dataclasses import asdict
from src.config import Settings
from python_ms_core import Core
from src.models.confidence_request import ConfidenceRequest
from src.service.osw_confidence_metric_calculator import OSWConfidenceMetricCalculator
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_response import ConfidenceResponse, ResponseData

logging.basicConfig()


class OSWConfidenceService:
    """
    OSWConfidenceService class is responsible for handling confidence calculation requests.

    Attributes:
    - `settings` (Settings): An instance of the Settings class for configuration parameters.
    - `incoming_topic` (Topic): Topic for incoming confidence calculation requests.
    - `outgoing_topic` (Topic): Topic for outgoing confidence calculation responses.
    - `storage_client` (StorageClient): Client for interacting with the storage service.
    - `logger` (Logger): Logger instance for logging service-specific information.

    Methods:
    - `__init__(self)`: Initializes an instance of the OSWConfidenceService class.
    - `subscribe(self) -> None`: Subscribes the service to the incoming confidence calculation topic.
    - `process(self, msg: QueueMessage)`: Processes incoming confidence calculation requests.
    - `calculate_confidence(self, request: ConfidenceRequest)`: Initiates the confidence calculation process.
    - `download_single_file(self, remote_url: str, local_path: str)`: Downloads a single file from a remote URL.
    - `send_response_message(self, response: ConfidenceResponse)`: Sends the confidence calculation response message.

    Usage:
    ```python
    # Example usage of the OSWConfidenceService class
    confidence_service = OSWConfidenceService()
    confidence_service.subscribe()
    ```
    """

    def __init__(self):
        """
        Initializes an instance of the OSWConfidenceService class.
        """
        core = Core()
        self.settings = Settings()
        self.incoming_topic = core.get_topic(self.settings.incoming_topic_name)
        self.outgoing_topic = core.get_topic(self.settings.outgoing_topic_name)
        self.storage_client = core.get_storage_client()
        self.logger = logging.getLogger('OSWConfService')
        self.subscribe()
        self.logger.setLevel(logging.INFO)
        self.logger.info('Confidence service initiated')
        self.logger.info('Downloads folder ')
        self.logger.info(self.settings.get_download_folder())
        # Make the downloads folder if it does not exist
        if not os.path.exists(self.settings.get_download_folder()):
            os.makedirs(self.settings.get_download_folder())
        if self.settings.is_simulated():
            self.logger.info('Simulated')
        else:
            self.logger.info('Not simulated')
        self.logger.info(self.settings.is_simulated())
        self.logger.info(self.settings.simulate)

    def subscribe(self) -> None:
        """
        Subscribes the service to the incoming confidence calculation topic.
        """
        self.logger.info('Start subscribing.')
        self.incoming_topic.subscribe(self.settings.incoming_topic_subscription, self.process)

    def process(self, msg: QueueMessage):
        """
        Processes incoming confidence calculation requests.

        Parameters:
        - `msg` (QueueMessage): The incoming queue message.
        """
        self.logger.info('Confidence calculation request received')
        self.logger.info(msg)
        # Have to start with the processing of the message
        try:
            confidence_request = ConfidenceRequest(messageType=msg.messageType, messageId=msg.messageId, data=msg.data)
            # create a thread and complete the message
            process_thread = threading.Thread(target=self.calculate_confidence, args=[confidence_request])
            process_thread.start()
        except TypeError as e:
            self.logger.error(' Type error occurred')
            self.logger.error(e)
            self.logger.error(msg)

    def calculate_confidence(self, request: ConfidenceRequest):
        """
        Initiates the confidence calculation process.

        Parameters:
        - `request` (ConfidenceRequest): The confidence calculation request.
        """
        local_base_path = os.path.join(self.settings.get_download_folder(), request.data.jobId)
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)
        
        if not self.settings.is_simulated() :

            # make a directory for the request
            jobId = request.data.jobId

            osw_file_local_path = os.path.join(local_base_path, f'{jobId}.zip')
            self.download_single_file(request.data.data_file, osw_file_local_path)
            
            # if regions file is not null, then download it as well
            sub_regions_file_local_path = None
            if request.data.sub_regions_file:
                sub_regions_file_local_path = os.path.join(local_base_path, f'{jobId}_subregions.geojson')
                self.download_single_file(request.data.sub_regions_file, sub_regions_file_local_path)

            metric = OSWConfidenceMetricCalculator(output_path=local_base_path, zip_file=osw_file_local_path, job_id=jobId, sub_regions_file=sub_regions_file_local_path)

            # Calculate the score using calculate_score method
            scores = metric.calculate_score()

            # Use the obtained score in your function
            self.logger.info('Score from OSWConfidenceMetricCalculator:', scores)
            
            # clean up
            metric.clean_up_files()
            self.logger.info(' Cleaned up the temp directory')
            
            is_success = False
            if scores is not None:
                is_success = True
            
            response = ConfidenceResponse(
                messageId=request.messageId,
                messageType=request.messageType,
                data=ResponseData(
                    jobId=jobId,
                    confidence_scores=scores,
                    confidence_library_version=osw_confidence_metric.__version__,
                    status='finished',
                    message='Processed successfully' if is_success else 'Processed failed',
                    success=is_success
                ).__dict__
            )

            self.logger.info('Sending response for lib confidence')
            self.send_response_message(response=response)
        else : # Simulated
            scores = json.loads('{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"confidence_score": 0.75}, "geometry": {"type": "Polygon", "coordinates": [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422],  [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}')
            jobId = request.data.jobId
            is_success = True
            response = ConfidenceResponse(
            messageId=request.messageId,
            messageType=request.messageType,
            data=ResponseData(
                jobId=jobId,
                confidence_scores=scores,
                confidence_library_version=osw_confidence_metric.__version__,
                status='finished',
                message='Processed successfully' if is_success else 'Processed failed',
                success=is_success
            ).__dict__
            )

            print(response)
            self.logger.info('Sending response for dummy confidence')
            self.send_response_message(response=response)

    def download_single_file(self, remote_url: str, local_path: str):
        """
        Downloads a single file from a remote URL.

        Parameters:
        - `remote_url` (str): The remote URL of the file.
        - `local_path` (str): The local path where the file should be saved.
        """
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

    def send_response_message(self, response: ConfidenceResponse):
        """
        Sends the confidence calculation response message.

        Parameters:
        - `response` (ConfidenceResponse): The confidence calculation response.
        """
        queue_message = QueueMessage.data_from({
            'messageId': response.messageId,
            'messageType': response.messageType,
            'data': asdict(response.data)
        })
        self.outgoing_topic.publish(queue_message)

# Service that handles the confidence calculation
import os
import json
import logging
import osw_confidence_metric
from dataclasses import asdict
from src.config import Settings
from python_ms_core import Core
from src.models.confidence_request import ConfidenceRequest
from src.service.osw_confidence_metric_calculator import OSWConfidenceMetricCalculator
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_response import ConfidenceResponse, ResponseData

logging.basicConfig()
logger = logging.getLogger("OSWConfService")
logger.setLevel(logging.INFO)


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
        self.core = Core()
        self.settings = Settings()
        self.incoming_topic = self.core.get_topic(self.settings.incoming_topic_name, max_concurrent_messages=self.settings.max_concurrent_messages)
        self.storage_client = self.core.get_storage_client()
        self.subscribe()
        logger.info('Confidence service initiated')
        logger.info('Downloads folder ')
        logger.info(self.settings.get_download_folder())
        # Make the downloads folder if it does not exist
        if not os.path.exists(self.settings.get_download_folder()):
            os.makedirs(self.settings.get_download_folder())
        if self.settings.is_simulated():
            logger.info('Simulated')
        else:
            logger.info('Not simulated')
        logger.info(self.settings.is_simulated())
        logger.info(self.settings.simulate)

    def subscribe(self) -> None:
        """
        Subscribes the service to the incoming confidence calculation topic.
        """
        logger.info('Start subscribing.')
        self.incoming_topic.subscribe(self.settings.incoming_topic_subscription, self.process)

    def process(self, msg: QueueMessage):
        """
        Processes incoming confidence calculation requests.

        Parameters:
        - `msg` (QueueMessage): The incoming queue message.
        """
        logger.info('Confidence calculation request received')
        logger.info(msg)
        # Have to start with the processing of the message
        try:
            confidence_request = ConfidenceRequest(messageType=msg.messageType, messageId=msg.messageId, data=msg.data)
            # create a thread and complete the message
            self.calculate_confidence(request=confidence_request)
        except TypeError as e:
            logger.error(' Type error occurred')
            logger.error(e)
            logger.error(msg)
            self.send_response_message(ConfidenceResponse(
                messageId=msg.messageId,
                messageType=msg.messageType,
                data=ResponseData(
                    jobId=msg.data['jobId'],
                    confidence_scores=None,
                    confidence_library_version=osw_confidence_metric.__version__,
                    status='finished',
                    message='Failed to process the request due to parsing error',
                    success=False
                ).__dict__
            ))

    def calculate_confidence(self, request: ConfidenceRequest):
        """
        Initiates the confidence calculation process.

        Parameters:
        - `request` (ConfidenceRequest): The confidence calculation request.
        """
        local_base_path = os.path.join(self.settings.get_download_folder(), request.data.jobId)
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)
        
        jobId = request.data.jobId
        is_success = False
        scores = None

        try:
            if not self.settings.is_simulated() :
                osw_file_local_path = os.path.join(local_base_path, f'{jobId}.zip')
                self.download_single_file(request.data.data_file, osw_file_local_path)
                
                sub_regions_file_local_path = None
                if request.data.sub_regions_file:
                    sub_regions_file_local_path = os.path.join(local_base_path, f'{jobId}_subregions.geojson')
                    self.download_single_file(request.data.sub_regions_file, sub_regions_file_local_path)

                metric = OSWConfidenceMetricCalculator(output_path=local_base_path, zip_file=osw_file_local_path, job_id=jobId, sub_regions_file=sub_regions_file_local_path)

                scores = metric.calculate_score()
                logger.info('Score from OSWConfidenceMetricCalculator:', scores)
                
                metric.clean_up_files()
                logger.info(' Cleaned up the temp directory')
                
                if scores is not None:
                    is_success = True
            else : # Simulated
                scores = json.loads('{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"confidence_score": 0.75}, "geometry": {"type": "Polygon", "coordinates": [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422],  [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}')
                is_success = True
        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            failed_message = f'Failed to calculate confidence : {e}'

        response = ConfidenceResponse(
            messageId=request.messageId,
            messageType=request.messageType,
            data=ResponseData(
                jobId=jobId,
                confidence_scores=scores,
                confidence_library_version=osw_confidence_metric.__version__,
                status='finished',
                message='Processed successfully' if is_success else failed_message,
                success=is_success
            ).__dict__
        )

        logger.info('Sending response for lib confidence')
        self.send_response_message(response=response)

    def download_single_file(self, remote_url: str, local_path: str):
        """
        Downloads a single file from a remote URL.

        Parameters:
        - `remote_url` (str): The remote URL of the file.
        - `local_path` (str): The local path where the file should be saved.
        """
        logger.info(f'Downloading {remote_url}')
        logger.info(f' to  {local_path}')
        file = self.storage_client.get_file_from_url(self.settings.storage_container_name, remote_url)

        try:
            if file.file_path:
                with open(local_path, 'wb') as blob:
                    blob.write(file.get_stream())
                logger.info(' File downloaded ')
            else:
                logger.info(f'File path not found at {local_path}')
        except Exception as e:
            logger.error(e)

    def send_response_message(self, response: ConfidenceResponse):
        """
        Sends the confidence calculation response message.

        Parameters:
        - `response` (ConfidenceResponse): The confidence calculation response.
        """
        try:
            queue_message = QueueMessage.data_from({
                'messageId': response.messageId,
                'messageType': response.messageType,
                'data': asdict(response.data)
            })
            self.core.get_topic(self.settings.outgoing_topic_name).publish(data=queue_message)
            logging.info(f'Published response for {response.data.jobId}')
        except Exception as e:
            logging.error(f'Failed to publish response: {e} for {response.data.jobId}')


import os
import json
import shutil
import zipfile
import unittest
from pathlib import Path
import osw_confidence_metric
from tempfile import TemporaryDirectory
from unittest.mock import Mock, MagicMock, patch
from src.service.osw_confidence_service import OSWConfidenceService
from src.service.osw_confidence_metric_calculator import OSWConfidenceMetricCalculator
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_request import ConfidenceRequest, RequestData
from src.models.confidence_response import ConfidenceResponse, ResponseData

FILE_PATH = f'{Path.cwd()}/tests/files/incoming_message.json'
ZIP_FILE_PATH = f'{Path.cwd()}/tests/files/osw.zip'
TEST_FILE = open(FILE_PATH)
TEST_DATA = json.loads(TEST_FILE.read())
DOWNLOAD_PATH = f'{Path.cwd()}/src/downloads'



class TestOSWConfidenceService(unittest.TestCase):

    def setUp(self) -> None:
        with patch.object(OSWConfidenceService, '__init__', return_value=None):
            self.service = OSWConfidenceService()
            self.service.incoming_topic = MagicMock()
            self.service.incoming_topic.subscribe = MagicMock()
            self.service.outgoing_topic = MagicMock()
            self.service.storage_client = MagicMock()
            self.service.logger = MagicMock()
            self.service.settings = MagicMock()
            self.service.settings.get_download_folder = MagicMock()
            self.service.settings.get_download_folder.return_value = DOWNLOAD_PATH
            # self.service.calculate_confidence = MagicMock()
            # self.service.calculate_confidence.return_value = 0.75

    def create_sample_zip_file(self, test_zip_file_path):
        shutil.copy(ZIP_FILE_PATH, test_zip_file_path)


    @patch.object(OSWConfidenceService, 'subscribe')
    def test_start_listening(self, mock_subscribe):
        # Act
        self.service.subscribe()

        # Assert
        mock_subscribe.assert_called_once()

    @patch('threading.Thread')
    def test_process_success(self, mock_thread):
        msg_data = TEST_DATA
        msg = QueueMessage.data_from(msg_data)

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        self.service.process(msg)

        mock_thread.assert_called_once_with(target=self.service.calculate_confidence,
                                            args=[ConfidenceRequest(**msg_data)])
        mock_thread_instance.start.assert_called_once()

    @patch.object(OSWConfidenceService, 'download_single_file')
    @patch('osw_confidence_metric.osm_data_handler.OSMDataHandler')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer.calculate_area_confidence_score')
    @patch.object(OSWConfidenceService, 'send_response_message')
    def test_calculate_confidence(self, mock_send_response_message, mock_score_calculation, mock_area_analyzer, mock_osm_data_handler,
                                  mock_download_single_file):
        msg_data = TEST_DATA
        request = ConfidenceRequest(**msg_data)
        job_id = request.data.jobId
        zip_file_path = f'{DOWNLOAD_PATH}/{job_id}.zip'
        self.create_sample_zip_file(zip_file_path)

        mock_download_single_file.return_value = zip_file_path
        mock_osm_data_handler_instance = MagicMock()
        mock_area_analyzer_instance = MagicMock()
        mock_area_analyzer_instance.calculate_area_confidence_score.return_value = 0.75
        mock_area_analyzer.return_value = mock_area_analyzer_instance
        mock_osm_data_handler.return_value = mock_osm_data_handler_instance
        mock_score_calculation.return_value = 0.75

        self.service.calculate_confidence(request=request)

        response = ConfidenceResponse(
            messageId=request.messageId,
            messageType=request.messageType,
            data=ResponseData(
                jobId=job_id,
                confidence_level=0.75,
                confidence_library_version=osw_confidence_metric.__version__,
                status='finished',
                message='Processed successfully',
                success=True
            ).__dict__
        )

        mock_send_response_message.assert_called_once_with(response=response)

    @patch('threading.Thread')
    def test_process_failure(self, mock_thread):
        msg_data = {'messageType': 'confidence-calculation', 'data': {}}
        msg = QueueMessage.data_from(msg_data)

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        self.service.process(msg)

        mock_thread.assert_not_called()

    def test_send_response_message(self):
        msg_data = TEST_DATA
        request = ConfidenceRequest(**msg_data)
        job_id = request.data.jobId
        response = ConfidenceResponse(
            messageId=request.messageId,
            messageType=request.messageType,
            data=ResponseData(
                jobId=job_id,
                confidence_level=0.75,
                confidence_library_version=osw_confidence_metric.__version__,
                status='finished',
                message='Processed successfully',
                success=True
            ).__dict__
        )

        self.service.send_response_message(response=response)


class TestOSWConfidenceServiceDownload(unittest.TestCase):
    @patch.object(OSWConfidenceService, 'download_single_file')
    def setUp(self, mock_download_single_file):
        file_path = FILE_PATH

        with patch.object(OSWConfidenceService, '__init__', return_value=None):
            self.service = OSWConfidenceService()
            self.service.logger = MagicMock()
            self.service.settings = MagicMock()
            self.service.settings.storage_container_name = MagicMock()
            self.service.settings.storage_container_name.return_value = 'test'
            self.service.storage_client = MagicMock()
            mock_download_single_file.return_value = file_path

    def tearDown(self):
        pass

    def test_download_single_file(self):
        # Arrange
        file_upload_path = f'{DOWNLOAD_PATH}/text_file.txt'
        self.service.storage_client = MagicMock()
        self.service.storage_client.get_file_from_url = MagicMock()
        file = MagicMock()
        file.file_path = file_upload_path
        file.get_stream = MagicMock(return_value=b'file_content')
        self.service.storage_client.get_file_from_url.return_value = file

        # Act
        self.service.download_single_file(remote_url=file_upload_path,
                                          local_path=file_upload_path)

        # Assert
        self.service.storage_client.get_file_from_url.assert_called_once_with(
            self.service.settings.storage_container_name,
            file_upload_path)

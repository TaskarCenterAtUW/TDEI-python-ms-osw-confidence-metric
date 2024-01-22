import os
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, create_autospec
from src.models.confidence_request import ConfidenceRequest
from src.service.osw_confidence_service import OSWConfidenceService
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_response import ConfidenceResponse, ResponseData

FILE_PATH = f'{Path.cwd()}/tests/files/incoming_message.json'
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

    @patch('threading.Thread')
    def test_process_failure(self, mock_thread):
        msg_data = {'messageType': 'confidence-calculation', 'data': {}}
        msg = QueueMessage.data_from(msg_data)

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        self.service.process(msg)

        mock_thread.assert_not_called()

    @patch.object(OSWConfidenceService, 'send_response_message')
    def test_send_response_message(self, mock_send_response_message):
        response = ConfidenceResponse(
            messageId='123',
            messageType='confidence_message',
            data=ResponseData(
                jobId='0b41ebc5-350c-42d3-90af-3af4ad3628fb',
                confidence_level='90.0',
                confidence_library_version='v1.0',
                status='finished',
                message='Processed successfully',
                success=True
            ).__dict__
        )

        self.service.send_response_message(response=response)

        mock_send_response_message.assert_called_once_with(response=response)


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

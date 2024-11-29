import os
import json
import shutil
import unittest
from pathlib import Path
import osw_confidence_metric
from unittest.mock import Mock, MagicMock, patch
from src.service.osw_confidence_service import OSWConfidenceService
from python_ms_core.core.queue.models.queue_message import QueueMessage
from src.models.confidence_request import ConfidenceRequest
from src.models.confidence_response import ConfidenceResponse, ResponseData

FILE_PATH = f'{Path.cwd()}/tests/files/incoming_message.json'
ZIP_FILE_PATH = f'{Path.cwd()}/tests/files/osw.zip'
TEST_FILE = open(FILE_PATH)
TEST_DATA = json.loads(TEST_FILE.read())
DOWNLOAD_PATH = f'{Path.cwd()}/downloads'


def create_sample_zip_file(test_zip_file_path):
    shutil.copy(ZIP_FILE_PATH, test_zip_file_path)


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
            os.makedirs(DOWNLOAD_PATH, exist_ok=True)

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

        # mock_thread.assert_called_once_with(target=self.service.calculate_confidence,
        #                                     args=[ConfidenceRequest(**msg_data)])
        # mock_thread_instance.start.assert_called_once()

    @patch.object(OSWConfidenceService, 'download_single_file')
    @patch('osw_confidence_metric.osm_data_handler.OSMDataHandler')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer.calculate_area_confidence_score')
    @patch.object(OSWConfidenceService, 'send_response_message')
    def test_calculate_confidence(self, mock_send_response_message, mock_score_calculation, mock_area_analyzer,
                                  mock_osm_data_handler,
                                  mock_download_single_file):
        msg_data = TEST_DATA
        request = ConfidenceRequest(**msg_data)
        job_id = request.data.jobId
        zip_file_path = f'{DOWNLOAD_PATH}/{job_id}.zip'
        create_sample_zip_file(zip_file_path)

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
                confidence_scores=json.loads(
                    '{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"confidence_score": 0.75}, "geometry": {"type": "Polygon", "coordinates": [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422],  [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}'),
                confidence_library_version=osw_confidence_metric.__version__,
                status='finished',
                message='Processed successfully',
                success=True
            ).__dict__
        )

        mock_send_response_message.assert_called_once_with(response=response)

    @patch('threading.Thread')
    def test_process_failure(self, mock_thread):
        msg_data = {'messageType': 'confidence-calculation', 'data': {'jobId': 123}}
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
                confidence_scores=0.75,
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

    def test_download_single_file_with_exception(self):
        # Arrange
        file_upload_path = f'{DOWNLOAD_PATH}/text_file.txt'
        self.service.storage_client = MagicMock()
        self.service.storage_client.get_file_from_url = MagicMock()
        self.service.storage_client.get_file_from_url.side_effect = Exception('Mock Error')

        # Act
        self.service.download_single_file(remote_url=file_upload_path,
                                          local_path=file_upload_path)

        self.service.storage_client.get_file_from_url.assert_called_once()


class TestOSWConfidenceServiceOther(unittest.TestCase):
    @patch('src.service.osw_confidence_service.Settings')
    @patch('src.service.osw_confidence_service.Core')
    def setUp(self, mock_core, mock_settings):
        mock_settings.return_value.incoming_topic_subscription = 'test_subscription'
        mock_settings.return_value.incoming_topic_name = 'test_request_topic'
        mock_settings.return_value.outgoing_topic_name = 'test_response_topic'
        mock_settings.return_value.max_concurrent_messages = 10
        mock_settings.return_value.storage_container_name = 'test_container'
        mock_settings.return_value.simulate = 'YES'

        # Mock Core
        mock_core.return_value.get_topic.return_value = MagicMock()
        mock_core.return_value.get_storage_client.return_value = MagicMock()

        self.core = mock_core

        self.service = OSWConfidenceService()
        self.service.storage_client = MagicMock()

        self.sample_message = {
            'messageId': '1234',
            'messageType': 'message type',
            'data': {
                'jobId': '1234',
                'data_file': 'https://tdeisamplestorage.blob.core.windows.net/confidence/tests/success_1_all_attrs.zip',
                'meta_file': 'https://tdeisamplestorage.blob.core.windows.net/confidence/tests/meta.geojson.zip',
                'trigger_type': 'manual',
                'sub_regions_file': 'https://tdeisamplestorage.blob.core.windows.net/confidence/tests/sub_regions_file.geojson',
            }
        }

    def test_subscribe(self):
        self.service.incoming_topic = MagicMock()
        self.service.incoming_topic.subscribe = MagicMock()

        self.service.subscribe()
        self.service.incoming_topic.subscribe.assert_called_once()

    def test_calculate_confidence_with_simulation(self):
        # Arrange
        self.service.send_response_message = MagicMock()
        request_msg = ConfidenceRequest(
            messageType=self.sample_message['messageType'],
            messageId=self.sample_message['messageId'],
            data={
                "jobId": self.sample_message['data']['jobId'],
                "data_file": self.sample_message['data']['data_file'],
                "meta_file": self.sample_message['data']['meta_file'],
                "trigger_type": self.sample_message['data']['trigger_type'],
                "sub_regions_file": self.sample_message['data']['sub_regions_file']
            }
        )

        # Act
        self.service.calculate_confidence(request_msg)

        # Assert
        self.service.send_response_message.assert_called_once()

    @patch('src.service.osw_confidence_service.OSWConfidenceMetricCalculator')
    def test_calculate_confidence_without_simulation(self, mock_calculator):
        # Arrange
        self.service.send_response_message = MagicMock()
        self.service.settings.is_simulated = MagicMock(return_value=False)

        expected_downloaded_file_path = "mock_path.zip"
        self.service.download_single_file = MagicMock(return_value=expected_downloaded_file_path)

        request_msg = ConfidenceRequest(
            messageType=self.sample_message['messageType'],
            messageId=self.sample_message['messageId'],
            data={
                "jobId": self.sample_message['data']['jobId'],
                "data_file": self.sample_message['data']['data_file'],
                "meta_file": self.sample_message['data']['meta_file'],
                "trigger_type": self.sample_message['data']['trigger_type'],
                "sub_regions_file": self.sample_message['data']['sub_regions_file']
            }
        )

        mock_calculator.return_value.calculate_score.return_value = '{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"confidence_score": 0.75}, "geometry": {"type": "Polygon", "coordinates": [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422],  [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}'
        mock_calculator.return_value.clean_up_files = MagicMock()

        # Act
        self.service.calculate_confidence(request_msg)

        # Assert
        self.service.send_response_message.assert_called_once()

    @patch('src.service.osw_confidence_service.OSWConfidenceMetricCalculator')
    def test_calculate_confidence_without_simulation_exception(self, mock_calculator):
        # Arrange
        self.service.send_response_message = MagicMock()
        self.service.settings.is_simulated = MagicMock(return_value=False)

        expected_downloaded_file_path = "mock_path.zip"
        self.service.download_single_file = MagicMock(return_value=expected_downloaded_file_path)

        request_msg = ConfidenceRequest(
            messageType=self.sample_message['messageType'],
            messageId=self.sample_message['messageId'],
            data={
                "jobId": self.sample_message['data']['jobId'],
                "data_file": self.sample_message['data']['data_file'],
                "meta_file": self.sample_message['data']['meta_file'],
                "trigger_type": self.sample_message['data']['trigger_type'],
                "sub_regions_file": self.sample_message['data']['sub_regions_file']
            }
        )

        mock_calculator.return_value.calculate_score.side_effect = Exception('Mocked exception')
        mock_calculator.return_value.clean_up_files = MagicMock()

        # Act
        self.service.calculate_confidence(request_msg)

        # Assert
        self.service.send_response_message.assert_called_once()

    @patch('src.service.osw_confidence_service.threading.Thread')
    def test_stop_listening(self, mock_thread):
        # Arrange
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        self.service.listening_thread = mock_thread_instance

        # Act
        result = self.service.stop_listening()

        # Assert
        mock_thread_instance.join.assert_called_once_with(timeout=0)
        self.assertIsNone(result)

    @patch('src.service.osw_confidence_service.QueueMessage')
    def test_send_response_message(self, mock_queue_message):
        # Arrange
        response_data = ResponseData(
            jobId='1234',
            confidence_scores=0.75,
            confidence_library_version=osw_confidence_metric.__version__,
            status='finished',
            message='Processed successfully',
            success=True
        )
        response = ConfidenceResponse(
            messageId='1234',
            messageType='message type',
            data=response_data.__dict__
        )
        mock_queue_message.data_from.return_value = MagicMock()
        mock_topic = self.service.core.get_topic.return_value
        mock_publish = mock_topic.publish

        # Act
        self.service.send_response_message(response=response)

        # Assert
        mock_queue_message.data_from.assert_called_once_with({
            'messageId': response.messageId,
            'messageType': response.messageType,
            'data': response_data.__dict__
        })
        mock_publish.assert_called_once()
        mock_topic.publish.assert_called_once_with(data=mock_queue_message.data_from.return_value)


if __name__ == '__main__':
    unittest.main()

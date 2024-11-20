import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch, mock_open
from src.service.helper import clean_up, is_valid_geojson
from jsonschema import ValidationError


class TestCleanUpFunction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_up_file(self):
        # Test clean_up function for a file
        test_file_path = os.path.join(self.temp_dir.name, 'test_file.txt')

        # Create a test file
        with open(test_file_path, 'w') as test_file:
            test_file.write('Test content')

        # Perform the clean-up
        clean_up(test_file_path)

        # Assertions
        self.assertFalse(os.path.exists(test_file_path))

    def test_clean_up_folder(self):
        # Test clean_up function for a folder
        test_folder_path = os.path.join(self.temp_dir.name, 'test_folder')

        # Create a test folder
        os.mkdir(test_folder_path)

        # Perform the clean-up
        clean_up(test_folder_path)

        # Assertions
        self.assertFalse(os.path.exists(test_folder_path))

    def test_clean_up_nonexistent_path(self):
        # Test clean_up function for a nonexistent path
        test_nonexistent_path = os.path.join(self.temp_dir.name, 'nonexistent_path')

        # Perform the clean-up
        clean_up(test_nonexistent_path)

        # Assertions
        self.assertFalse(os.path.exists(test_nonexistent_path))

    @patch('builtins.print')
    def test_clean_up_prints_messages(self, mock_print):
        # Test clean_up function prints messages when removing files and folders
        test_file_path = os.path.join(self.temp_dir.name, 'test_file.txt')
        test_folder_path = os.path.join(self.temp_dir.name, 'test_folder')

        # Create a test file and folder
        with open(test_file_path, 'w') as test_file:
            test_file.write('Test content')
        os.mkdir(test_folder_path)

        # Perform the clean-up
        clean_up(test_file_path)
        clean_up(test_folder_path)

        # Assertions
        mock_print.assert_any_call(f' Removing File: {test_file_path}')
        mock_print.assert_any_call(f' Removing Folder: {test_folder_path}')


class TestIsValidGeoJSON(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"type": "FeatureCollection", "features": []}')
    @patch('requests.get')
    @patch('src.service.helper.validate')
    def test_valid_geojson(self, mock_validate, mock_requests_get, mock_open_file):
        # Arrange
        geojson_schema_url = 'https://geojson.org/schema/FeatureCollection.json'
        schema = {'type': 'object'}  # Example mock schema
        mock_requests_get.return_value.json.return_value = schema  # Mock schema response
        file_path = '/path/to/valid.geojson'

        # Act
        result = is_valid_geojson(file_path)

        # Assert
        mock_open_file.assert_called_once_with(file_path, 'r')  # Verify file is opened
        mock_requests_get.assert_called_once_with(geojson_schema_url)  # Verify schema fetch
        mock_validate.assert_called_once_with(
            instance={'type': 'FeatureCollection', 'features': []}, schema=schema
        )  # Check validation call
        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data='invalid_json')
    @patch('requests.get')
    def test_is_valid_geojson_invalid_json(self, mock_requests_get, mock_open_file):
        # Arrange
        file_path = '/path/to/invalid.geojson'

        # Act
        result = is_valid_geojson(file_path)

        # Assert
        mock_open_file.assert_called_once_with(file_path, 'r')
        self.assertFalse(result)

    @patch('builtins.open', new_callable=mock_open, read_data='{"type": "FeatureCollection", "features": []}')
    @patch('requests.get')
    @patch('src.service.helper.validate', side_effect=ValidationError('Invalid GeoJSON'))
    def test_is_valid_geojson_invalid_geojson(self, mock_validate, mock_requests_get, mock_open_file):
        # Arrange
        geojson_schema_url = 'https://geojson.org/schema/FeatureCollection.json'
        schema = {'type': 'object'}
        mock_requests_get.return_value.json.return_value = schema
        file_path = '/path/to/invalid.geojson'

        # Act
        result = is_valid_geojson(file_path)

        # Assert
        mock_open_file.assert_called_once_with(file_path, 'r')
        mock_requests_get.assert_called_once_with(geojson_schema_url)
        mock_validate.assert_called_once()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

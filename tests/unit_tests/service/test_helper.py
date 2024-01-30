import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from src.service.helper import clean_up


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


if __name__ == '__main__':
    unittest.main()

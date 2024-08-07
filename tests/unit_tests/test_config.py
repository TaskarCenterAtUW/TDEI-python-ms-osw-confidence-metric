import os
import unittest
from pathlib import Path
from src.config import Settings

DOWNLOAD_PATH = f'{Path.cwd()}/src/downloads'


class TestSettings(unittest.TestCase):

    def test_settings_instantiation(self):
        # Act
        settings_instance = Settings()

        # Assert
        self.assertEqual(settings_instance.app_name, 'osw-confidence-metric-service-python')
        self.assertIsInstance(settings_instance, Settings)

    def test_get_download_folder(self):
        # Arrange
        settings_instance = Settings()

        # Act
        download_folder = settings_instance.get_download_folder()
        # Assert

        self.assertEqual(download_folder, DOWNLOAD_PATH)


if __name__ == '__main__':
    unittest.main()

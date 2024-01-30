import os
import zipfile
import unittest
from src.service.helper import clean_up
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock
from src.service.osw_confidence_metric_calculator import OSWConfidenceMetricCalculator


class TestOSWConfidenceMetric(unittest.TestCase):

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.zip_file_path = os.path.join(self.temp_dir.name, 'test_data.zip')
        self.create_sample_zip_file(self.zip_file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_sample_zip_file(self, zip_file_path):
        # Create a sample zip file for testing
        with zipfile.ZipFile(zip_file_path, 'w') as zip_ref:
            zip_ref.writestr('nodes.geojson',
                             '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"coordinates":[[[-122.32125181758033,47.62012777661363],[-122.32103130968568,47.6184432558874],[-122.31924624577745,47.61885377434356],[-122.3192147446495,47.62007823266089],[-122.32125181758033,47.62012777661363]]],"type":"Polygon"}}]}')
            zip_ref.writestr('other_file.txt', 'Some random content')

    @patch('osw_confidence_metric.osm_data_handler.OSMDataHandler')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer')
    def test_init(self, mock_area_analyzer, mock_osm_data_handler):
        # Test initialization of OSWConfidenceMetric
        confidence_metric = OSWConfidenceMetricCalculator(self.zip_file_path)
        self.assertEqual(confidence_metric.zip_file_path, self.zip_file_path)
        self.assertIsNotNone(confidence_metric.settings)
        self.assertIsNotNone(confidence_metric.username)
        self.assertIsNotNone(confidence_metric.password)
        self.assertIsNotNone(confidence_metric.output)
        self.assertIsNotNone(confidence_metric.nodes_file)
        self.assertIsNotNone(confidence_metric.extracted_files)
        self.assertIsNotNone(confidence_metric.convex_file)

    @patch('osw_confidence_metric.osm_data_handler.OSMDataHandler')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer.calculate_area_confidence_score')
    def test_calculate_score(self, mock_score_calculation,
                             mock_area_analyzer, mock_osm_data_handler):
        # Test calculate_score method
        confidence_metric = OSWConfidenceMetricCalculator(self.zip_file_path)

        # Mocking external dependencies
        mock_osm_data_handler_instance = MagicMock()
        mock_area_analyzer_instance = MagicMock()
        mock_area_analyzer_instance.calculate_area_confidence_score.return_value = 0.75
        mock_area_analyzer.return_value = mock_area_analyzer_instance
        mock_osm_data_handler.return_value = mock_osm_data_handler_instance
        mock_score_calculation.return_value = 0.75

        # Perform the test
        confidence_score = confidence_metric.calculate_score()

        # Assertions
        self.assertEqual(confidence_score, 0.75)

    def test_unzip_nodes_file(self):
        # Test unzip_nodes_file method
        confidence_metric = OSWConfidenceMetricCalculator(self.zip_file_path)

        # Perform the test
        nodes_file, extracted_files = confidence_metric.unzip_nodes_file()

        # Assertions
        self.assertEqual(nodes_file, os.path.join(confidence_metric.output, 'nodes.geojson'))
        self.assertEqual(extracted_files, ['nodes.geojson', 'other_file.txt'])

    def test_get_convex_hull(self):
        # Test get_convex_hull method
        confidence_metric = OSWConfidenceMetricCalculator(self.zip_file_path)

        # Perform the test
        convex_file = confidence_metric.get_convex_hull()

        # Assertions
        self.assertEqual(convex_file, os.path.join(confidence_metric.output, 'convex_hull.geojson'))


if __name__ == '__main__':
    unittest.main()

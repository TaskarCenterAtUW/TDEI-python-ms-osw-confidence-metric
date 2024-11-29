import os
import zipfile
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock, mock_open
from src.service.osw_confidence_metric_calculator import OSWConfidenceMetricCalculator


def create_sample_inputs(zip_file_path, sub_regions_file_path):
    # Create a sample zip file for testing
    with zipfile.ZipFile(zip_file_path, 'w') as zip_ref:
        zip_ref.writestr('nodes.geojson',
                         '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"coordinates":[[[-122.32125181758033,47.62012777661363],[-122.32103130968568,47.6184432558874],[-122.31924624577745,47.61885377434356],[-122.3192147446495,47.62007823266089],[-122.32125181758033,47.62012777661363]]],"type":"Polygon"}}]}')
        zip_ref.writestr('other_file.txt', 'Some random content')
    with open(sub_regions_file_path, 'w') as sub_file:
        sub_file.write(
            '{"type": "FeatureCollection","features": [{ "type": "Feature", "properties": { }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -122.6698850202686, 48.286157259313114 ], [ -122.63851879396184, 48.286157259313114 ],[ -122.63851879396184, 48.297497546405765 ], [-122.6698850202686,48.297497546405765 ], [ -122.6698850202686, 48.286157259313114 ] ] ] }  }]}')


class TestOSWConfidenceMetric(unittest.TestCase):

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.job_id = '1234'
        self.temp_path = os.path.join(self.temp_dir.name, self.job_id)
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        self.zip_file_path = os.path.join(self.temp_path, 'test_data.zip')
        self.sub_region_file_path = os.path.join(self.temp_path, 'sub_regions.geojson')
        create_sample_inputs(self.zip_file_path, self.sub_region_file_path)

    def tearDown(self):
        self.temp_dir.cleanup()


    @patch('osw_confidence_metric.osm_data_handler.OSMDataHandler')
    @patch('osw_confidence_metric.area_analyzer.AreaAnalyzer')
    def test_init(self, mock_area_analyzer, mock_osm_data_handler):
        # Test initialization of OSWConfidenceMetric
        confidence_metric = OSWConfidenceMetricCalculator(output_path=self.temp_path, zip_file=self.zip_file_path,
                                                          job_id=self.job_id,
                                                          sub_regions_file=self.sub_region_file_path)
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
        confidence_metric = OSWConfidenceMetricCalculator(output_path=self.temp_path, zip_file=self.zip_file_path,
                                                          job_id=self.job_id,
                                                          sub_regions_file=self.sub_region_file_path)

        # Mocking external dependencies
        mock_osm_data_handler_instance = MagicMock()
        mock_area_analyzer_instance = MagicMock()
        mock_area_analyzer_instance.calculate_area_confidence_score.return_value = 0.75
        mock_area_analyzer.return_value = mock_area_analyzer_instance
        mock_osm_data_handler.return_value = mock_osm_data_handler_instance
        mock_score_calculation.return_value = 0.75

        # Perform the test
        confidence_scores = confidence_metric.calculate_score()
        len_scores = len(confidence_scores["features"])
        self.assertEqual(len_scores, 2)
        one_conf_score = confidence_scores["features"][0]["properties"]["confidence_score"]

        # Assertions
        self.assertEqual(one_conf_score, 0.75)

    def test_unzip_nodes_file(self):
        confidence_metric = OSWConfidenceMetricCalculator(output_path=self.temp_path, zip_file=self.zip_file_path,
                                                          job_id=self.job_id)

        # Perform the test
        nodes_file, extracted_files = confidence_metric.unzip_nodes_file()

        # Assertions
        self.assertEqual(nodes_file, os.path.join(confidence_metric.output, 'nodes.geojson'))
        self.assertEqual(extracted_files, ['nodes.geojson', 'other_file.txt'])

    def test_get_convex_hull(self):
        # Test get_convex_hull method
        confidence_metric = OSWConfidenceMetricCalculator(output_path=self.temp_path, zip_file=self.zip_file_path,
                                                          job_id=self.job_id)

        # Perform the test
        convex_file = confidence_metric.get_convex_hull()

        # Assertions
        self.assertEqual(convex_file, os.path.join(confidence_metric.output, f'{self.job_id}.geojson'))

    @patch('src.service.osw_confidence_metric_calculator.clean_up')
    def test_clean_up_files(self, mock_clean_up):
        confidence_metric = OSWConfidenceMetricCalculator(output_path=self.temp_path, zip_file=self.zip_file_path,
                                                          job_id=self.job_id)

        confidence_metric.clean_up_files()

        mock_clean_up.assert_called_once_with(path=self.temp_path)


if __name__ == '__main__':
    unittest.main()

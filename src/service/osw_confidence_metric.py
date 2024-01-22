import os
import time
import zipfile
import warnings
import geopandas as gpd
from src.config import Settings
from src.service.helper import clean_up
from python_confidence_metric.area_analyzer import AreaAnalyzer
from python_confidence_metric.osm_data_handler import OSMDataHandler

warnings.filterwarnings('ignore', category=DeprecationWarning)

username = 'sujatam@gaussiansolutions.com'
password = 'R@lling#1'


class OSWConfidenceMetric:
    def __init__(self, zip_file):
        self.zip_file_path = zip_file
        self.settings = Settings()
        self.username = self.settings.username
        self.password = self.settings.password
        self.output = self.settings.get_download_folder()
        self.nodes_file, self.extracted_files = self.unzip_nodes_file()
        self.convex_file = self.get_convex_hull()

    def unzip_nodes_file(self):
        with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.output)
            extracted_files = zip_ref.namelist()
            print(extracted_files)
            required_files = ['nodes']
            file_locations = None

            for required_file in required_files:
                for extracted_file in extracted_files:
                    if '__MACOSX' in extracted_file:
                        continue
                    if required_file in extracted_file:
                        file_locations = f"{self.output}/{extracted_file}"

            return file_locations, extracted_files

    def get_convex_hull(self):
        gdf = gpd.read_file(self.nodes_file)
        merged_geometry = gdf.unary_union
        convex_hull = merged_geometry.convex_hull
        # Create a GeoDataFrame from the convex hull
        convex_hull_gdf = gpd.GeoDataFrame(geometry=[convex_hull])

        output_file = os.path.join(self.output, 'convex_hull.geojson')
        # Save the convex hull as a new GeoJSON file
        convex_hull_gdf.to_file(output_file, driver='GeoJSON')
        return output_file

    def calculate_score(self):
        print(self.__dict__)
        osm_data_handler = OSMDataHandler(username=username, password=password)
        area_analyzer = AreaAnalyzer(osm_data_handler=osm_data_handler)
        start_time = time.time()
        score = area_analyzer.calculate_area_confidence_score(file_path=self.convex_file)
        print("--- %s seconds ---" % (time.time() - start_time))
        clean_up(path=self.convex_file)
        for extracted_file in self.extracted_files:
            clean_up(path=extracted_file)
        return score


if __name__ == '__main__':
    _settings = Settings()
    zip_path = os.path.join(_settings.get_download_folder(), 'osw.zip')
    metric = OSWConfidenceMetric(zip_file=zip_path)
    score = metric.calculate_score()

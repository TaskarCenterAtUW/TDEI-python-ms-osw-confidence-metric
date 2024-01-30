import os
import time
import zipfile
import logging
import warnings
from typing import Tuple, List
import geopandas as gpd
from src.config import Settings
from src.service.helper import clean_up
from osw_confidence_metric.area_analyzer import AreaAnalyzer
from osw_confidence_metric.osm_data_handler import OSMDataHandler

logging.basicConfig()
warnings.filterwarnings('ignore', category=DeprecationWarning)


class OSWConfidenceMetric:
    """
    OSWConfidenceMetric class analyzes OpenStreetMap (OSM) node data to calculate a confidence score for a specified area.

    Attributes:
    - `zip_file_path` (str): The path to the input zip file containing OSM node data.
    - `settings` (Settings): An instance of the Settings class for configuration parameters.
    - `username` (str): OSM username obtained from the configuration settings.
    - `password` (str): OSM password obtained from the configuration settings.
    - `output` (str): Folder where extracted and processed files will be stored.
    - `nodes_file` (str): File path to the extracted nodes file from the input zip.
    - `extracted_files` (list): List of all files extracted from the input zip.
    - `convex_file` (str): File path to the GeoJSON file representing the convex hull of the extracted OSM nodes.

    Methods:
    - `unzip_nodes_file(self) -> Tuple[str, List[str]]`: Extracts the nodes file from the input zip, excluding unnecessary files and directories.
    - `get_convex_hull(self) -> str`: Reads the nodes file and calculates the convex hull of the node points, saving it as a GeoJSON file.
    - `calculate_score(self) -> float`: Initiates the process of calculating the confidence score for the area represented by the convex hull.

    Usage:
    ```python
    # Example usage of the OSWConfidenceMetric class
    zip_file_path = "path/to/osm_data.zip"
    confidence_metric = OSWConfidenceMetric(zip_file=zip_file_path)
    confidence_score = confidence_metric.calculate_score()
    print("Area Confidence Score:", confidence_score)
    ```
    """

    def __init__(self, zip_file: str):
        """
        Initializes an instance of the OSWConfidenceMetric class.

        Parameters:
        - `zip_file` (str): The path to the input zip file containing OSM node data.
        """
        self.zip_file_path = zip_file
        self.settings = Settings()
        self.username = self.settings.username
        self.password = self.settings.password
        self.output = self.settings.get_download_folder()
        self.nodes_file, self.extracted_files = self.unzip_nodes_file()
        self.convex_file = self.get_convex_hull()

    def unzip_nodes_file(self) -> Tuple[str, List[str]]:
        """
        Extracts the nodes file from the input zip, excluding unnecessary files and directories.

        Returns:
        - `file_locations` (str): File path to the extracted nodes file.
        - `extracted_files` (list): List of all files extracted from the input zip.
        """
        with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.output)
            extracted_files = zip_ref.namelist()
            required_files = ['nodes']
            file_locations = None

            for required_file in required_files:
                for extracted_file in extracted_files:
                    if '__MACOSX' in extracted_file:
                        continue
                    if required_file in extracted_file:
                        file_locations = f"{self.output}/{extracted_file}"

            return file_locations, extracted_files

    def get_convex_hull(self) -> str:
        """
        Reads the nodes file and calculates the convex hull of the node points, saving it as a GeoJSON file.

        Returns:
        - `output_file` (str): File path to the GeoJSON file representing the convex hull.
        """
        gdf = gpd.read_file(self.nodes_file)
        merged_geometry = gdf.unary_union
        convex_hull = merged_geometry.convex_hull
        convex_hull_gdf = gpd.GeoDataFrame(geometry=[convex_hull])

        output_file = os.path.join(self.output, 'convex_hull.geojson')
        convex_hull_gdf.to_file(output_file, driver='GeoJSON')
        return output_file

    def calculate_score(self) -> float:
        """
        Initiates the process of calculating the confidence score for the area represented by the convex hull.

        Returns:
        - `score` (float): The calculated confidence score.
        """
        osm_data_handler = OSMDataHandler(username=self.settings.username, password=self.settings.password)
        area_analyzer = AreaAnalyzer(osm_data_handler=osm_data_handler)
        start_time = time.time()
        score = area_analyzer.calculate_area_confidence_score(file_path=self.convex_file)
        logging.info("--- %s seconds ---" % (time.time() - start_time))
        clean_up(path=self.convex_file)
        for extracted_file in self.extracted_files:
            clean_up(path=os.path.join(self.output, extracted_file))
        clean_up(path=os.path.join(self.output, '__MACOSX'))
        return score

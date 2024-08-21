import json 
import os
import pandas as pd
import time
import zipfile
import logging
import warnings
from typing import Tuple, List
import geopandas as gpd
from src.config import Settings
from src.service.helper import clean_up, is_valid_geojson
from osw_confidence_metric.area_analyzer import AreaAnalyzer
from osw_confidence_metric.osm_data_handler import OSMDataHandler
import geojson


logging.basicConfig()
logger = logging.getLogger("OSWConfServiceMetricCalculation")
logger.setLevel(logging.INFO)
# warnings.filterwarnings('ignore', category=DeprecationWarning)
# warnings.simplefilter(action='ignore', category=FutureWarning)



class OSWConfidenceMetricCalculator:
    """
    OSWConfidenceMetricCalculator class analyzes OpenStreetMap (OSM) node data to calculate a confidence score for a specified area.

    Attributes:
    - `zip_file_path` (str): The path to the input zip file containing OSM node data.
    - `settings` (Settings): An instance of the Settings class for configuration parameters.
    - `username` (str): OSM username obtained from the configuration settings.
    - `password` (str): OSM password obtained from the configuration settings.
    - `output` (str): Folder where extracted and processed files will be stored.
    - `nodes_file` (str): File path to the extracted nodes file from the input zip.
    - `extracted_files` (list): List of all files extracted from the input zip.
    - `convex_file` (str): File path to the GeoJSON file representing the convex hull of the extracted OSM nodes.
    - `job_id` (str): A unique identifier.

    Methods:
    - `unzip_nodes_file(self) -> Tuple[str, List[str]]`: Extracts the nodes file from the input zip, excluding unnecessary files and directories.
    - `get_convex_hull(self) -> str`: Reads the nodes file and calculates the convex hull of the node points, saving it as a GeoJSON file.
    - `calculate_score(self) -> float`: Initiates the process of calculating the confidence score for the area represented by the convex hull.

    Usage:
    ```python
    # Example usage of the OSWConfidenceMetricCalculator class
    zip_file_path = "path/to/osm_data.zip"
    confidence_metric = OSWConfidenceMetricCalculator(zip_file=zip_file_path)
    confidence_score = confidence_metric.calculate_score()
    print("Area Confidence Score:", confidence_score)
    ```
    """

    def __init__(self, output_path: str, zip_file: str, job_id: str, sub_regions_file: str = None ):
        """
        Initializes an instance of the OSWConfidenceMetricCalculator class.

        Parameters:
        - `zip_file` (str): The path to the input zip file containing OSM node data.
        - `job_id` (str): The unique identifier.
        """
        self.zip_file_path = zip_file
        self.sub_regions_file = sub_regions_file
        self.job_id = job_id
        self.settings = Settings()
        self.username = self.settings.username
        self.password = self.settings.password
        self.output = output_path
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

        output_file = os.path.join(self.output, f'{self.job_id}.geojson')
        convex_hull_gdf.to_file(output_file, driver='GeoJSON')
        return output_file

    # def calculate_score(self) -> JSON:
    def calculate_score(self):
        """
        Initiates the process of calculating the confidence score for the area represented by the convex hull.

        Returns:
        - `results` (dict): geojson object with the first element being dataset convex hull, and the subsequent 
                ones are the given input areas in the subregions file, with confidence_score added to each of
                element's properties
        """
        
        osm_data_handler = OSMDataHandler(username=self.settings.username, password=self.settings.password)
        area_analyzer = AreaAnalyzer(osm_data_handler=osm_data_handler)
        start_time = time.time()
        score = area_analyzer.calculate_area_confidence_score(file_path=self.convex_file)
        # score = 0.75
        logger.info("--- %s seconds ---" % (time.time() - start_time))
        
        sub_regions_gdf = None
        if self.sub_regions_file:
            is_sub_region_file_valid = is_valid_geojson(self.sub_regions_file)
            if is_sub_region_file_valid:
                with open(self.sub_regions_file, "r") as file:
                    sub_regions = geojson.load(file)
                    # print(type(sub_regions))
                    # print((sub_regions))
                # print(sub_regions_gdf)
                sub_regions_gdf = gpd.read_file(self.sub_regions_file)
                conf_scores:List = []
                for index, feature in enumerate(sub_regions.features):
                    # print(index, feature)
                    start_time = time.time()
                    logger.info(" calculating confidence metric for sub_region: ", index, " of job_id: ", self.job_id)
                    if isinstance(feature, geojson.Feature) and isinstance(feature.geometry, geojson.Polygon):
                    # # if isinstance(feature, geojson.Feature):
                    # if isinstance(feature.geometry, geojson.Polygon):
                        split_ext = os.path.splitext(self.sub_regions_file)
                        temp_geojson_file_name = split_ext[0]+"_"+str(index)+split_ext[1]
                        
                        with open(temp_geojson_file_name, 'w') as outfile:
                            geojson.dump(feature, outfile)
                        sub_score = area_analyzer.calculate_area_confidence_score(file_path=temp_geojson_file_name)
                    else:
                        logger.info(" row: ", index, " of subregion is not a polygon. skipping cals..")
                        # print("skipping for ... ", index)
                        sub_score = None 
                        
                    logger.info("--- %s seconds ---" % (time.time() - start_time))
                    conf_scores.append(sub_score)
                
                # print("len of sub_regoions = ", len(sub_regions_gdf), " len of conf_socres =", len(conf_scores))
                sub_regions_gdf['confidence_score'] = conf_scores    
                
            else:
                logging.info("Error occurred in reading input subregions file: ")
                sub_regions_gdf = None
                        

        main_region_gdf = gpd.read_file(self.convex_file)
        assert(len(main_region_gdf) == 1)
        main_polygon = main_region_gdf.iloc[0].geometry
        main_result_gdf = gpd.GeoDataFrame([ {'geometry': main_polygon} ], crs=main_region_gdf.crs)
        main_result_gdf['confidence_score'] = [score]
        
        if sub_regions_gdf is not None:
            # main_result_gdf = main_result_gdf.append(sub_regions_gdf, ignore_index=True)
            main_result_gdf = pd.concat([main_result_gdf, sub_regions_gdf], ignore_index=True)
            
        # print(main_result_gdf)
        results = main_result_gdf.to_json()
        results = json.loads(results)
        return results

    def clean_up_files(self) -> None:
        clean_up(path=self.output)
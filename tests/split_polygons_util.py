import sys
import geopandas as gpd
from shapely.geometry import Polygon, box
import numpy as np

def split_polygon(polygon, n_splits):
    """Splits a polygon into n_splits non-overlapping polygons."""
    minx, miny, maxx, maxy = polygon.bounds
    width = maxx - minx
    height = maxy - miny
    nx = int(np.sqrt(n_splits * width / height))
    ny = n_splits // nx
    
    # Adjust to match exactly n_splits if needed
    while nx * ny < n_splits:
        nx += 1
    
    dx = width / nx
    dy = height / ny
    sub_polygons = []
    
    for i in range(nx):
        for j in range(ny):
            new_poly = box(minx + i * dx, miny + j * dy, minx + (i + 1) * dx, miny + (j + 1) * dy)
            intersection = new_poly.intersection(polygon)
            if not intersection.is_empty:
                sub_polygons.append(intersection)
    
    return sub_polygons

def main(input_geojson, output_geojson, n_splits):
    # Load the input GeoJSON
    gdf = gpd.read_file(input_geojson)
    
    # Assuming the input GeoJSON contains a single polygon
    input_polygon = gdf.iloc[0].geometry
    
    # Split the polygon
    sub_polygons = split_polygon(input_polygon, n_splits)
    
    # Create a new GeoDataFrame
    new_gdf = gpd.GeoDataFrame(geometry=sub_polygons)
    
    # Export to GeoJSON
    new_gdf.to_file(output_geojson, driver='GeoJSON')

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file> <output_file> <number_of_splits>")
        sys.exit(1)

    input_geojson = sys.argv[1]
    output_geojson = sys.argv[2]
    n_splits = int(sys.argv[3])  # Ensure this is an integer

    main(input_geojson, output_geojson, n_splits)

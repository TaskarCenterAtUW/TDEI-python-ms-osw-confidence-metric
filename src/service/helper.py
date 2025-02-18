import os
import shutil
import json
from jsonschema import validate, ValidationError
import requests

def clean_up(path):
    """
    Removes a specified file or directory from the filesystem.

    Parameters:
    - `path` (str): The path to the file or directory that needs to be removed.

    Behavior:
    - Checks if the specified path exists.
    - If the path points to a file:
      - Prints a message indicating the removal of the file.
      - Uses `os.remove(path)` to delete the file.a
    - If the path points to a directory:
      - Prints a message indicating the removal of the directory.
      - Uses `shutil.rmtree(path, ignore_errors=False)` to recursively remove the directory and its contents.
        - The `ignore_errors=False` parameter ensures that any errors during removal are not ignored, allowing the function to raise exceptions if needed.

    Usage:
    ```python
    # Example usage of the clean_up function
    file_path = "path/to/file.txt"
    folder_path = "path/to/folder"

    # Remove a file
    clean_up(file_path)

    # Remove a folder
    clean_up(folder_path)
    ```

    This function is particularly useful for managing temporary files and directories, providing a convenient way to clean up resources and maintain a clean filesystem. The print statements serve as informative messages, indicating the specific action taken by the function.
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            print(f' Removing File: {path}')
            os.remove(path)
        else:
            folder = os.path.join(path)
            print(f' Removing Folder: {path}')
            shutil.rmtree(folder, ignore_errors=False)

def is_valid_geojson(file_path):
    # Load the official GeoJSON schema
    geojson_schema_url = "https://geojson.org/schema/FeatureCollection.json"
    schema = requests.get(geojson_schema_url).json()
    
    # Read and parse the JSON data from the file
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("Invalid JSON format.")
        return False

    # Validate the GeoJSON data against the schema
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        print("Validation Error:", e)
        return False
# TDEI-python-ms-osw-confidence-metric

## Introduction
OSW Confidence metric service

## Requirements
python 3.10

## How to run the project with Python3.10
#### Create virtual env

`python3.10 -m venv .venv`

`source .venv/bin/activate`

#### Install requirements

`pip install -r requirements.txt`

#### Set up env file, create a .env file at project root level 

```shell
OSM_USERNAME=xxx
OSM_PASSWORD=xxx
PROVIDER=xxx
QUEUECONNECTION=Endpoint=sb://xxxxxxxxxxxxx
STORAGECONNECTION=DefaultEndpointsProtocol=https;xxxxxxxxxxxxx
CONFIDENCE_REQ_TOPIC=<Confidence request topic>
CONFIDENCE_REQ_SUB= <Confidence request subscription>
CONFIDENCE_RES_TOPIC=<Confidence response topic>
MAX_CONCURRENT_MESSAGES=xxx
```
Note: Replace the endpoints with the actual endpoints of the environment you want to run the service in

`MAX_CONCURRENT_MESSAGES` is the maximum number of concurrent messages that the service can handle. If not provided, defaults to 2

### Run the Server 

`uvicorn src.main:app --reload`

remove `--reload` for non-debug mode

### Run the examples

`python src/example.py`

### Run the Server

`uvicorn src.main:app --reload`

### Run Unit tests

####  Run Coverage
`python -m coverage run --source=src -m unittest discover -s tests/unit_tests`

To run a single test use

`python -m unittest tests.unit_tests.service.test_osw_confidence_metric_calculator.TestOSWConfidenceMetric.test_calculate_score`

####  Run Coverage Report
`coverage report`

####  Run Coverage HTML report
`coverage html`


### Incoming Request

```json
{
  "messageId": "0b41ebc5-350c-42d3-90af-3af4ad3628fb",
  "messageType": "confidence-calculation",
  "data":{
    "jobId": "0b41ebc5-350c-42d3-90af-3af4ad3628fb",
    "data_file": "https://tdeisamplestorage.blob.core.windows.net/osw/2023/03/0b41ebc5-350c-42d3-90af-3af4ad3628fb/osw_file.zip",
    "meta_file": "https://tdeisamplestorage.blob.core.windows.net/osw/2023/03/0b41ebc5-350c-42d3-90af-3af4ad3628fb/meta.json",
    "sub_regions_file": " <path to sub regions geojson file> ",
    "trigger_type": "manual"
  }
}
```

### Outgoing Request

```json
{
  "messageId": "0b41ebc5-350c-42d3-90af-3af4ad3628fb",
  "messageType":"confidence-calculation",
  "data":{
    "jobId":"0b41ebc5-350c-42d3-90af-3af4ad3628fb",
    "confidence_scores": "{'type': 'FeatureCollection', 'features': [{'id': '0', 'type': 'Feature', 'properties': {'confidence_score': 0.75}, 'geometry': {'type': 'Polygon', 'coordinates': [[[-122.1322201, 47.63528], [-122.1378655, 47.6353141], [-122.1395176, 47.6355614], [-122.1431969, 47.6365115], [-122.1443805, 47.6385402], [-122.1469453, 47.6460242], [-122.1429792, 47.6495373], [-122.1403351, 47.6497278], [-122.1325839, 47.6498422], [-122.1321999, 47.6496722], [-122.1321845, 47.6496558], [-122.1285859, 47.6378078], [-122.1322201, 47.63528]]]}}]}",
    "confidence_library_version": "v1.0",
    "status": "finished",
    "message": "Processed successfully",
    "success": true
  }
}
```

### Simulation
If you want to simulate the confidence calculation, add another environment variable with name
`SIMULATE_METRIC` and its value to `YES`

```
SIMULATE_METRIC=YES
```
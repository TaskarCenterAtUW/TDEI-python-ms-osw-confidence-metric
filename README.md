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
QUEUECONNECTION=Endpoint=sb://xxxxxxxxxxxxx
STORAGECONNECTION=DefaultEndpointsProtocol=https;xxxxxxxxxxxxx
CONFIDENCE_REQ_TOPIC=<Confidence request topic>
CONFIDENCE_REQ_SUB= <Confidence request subscription>
CONFIDENCE_RES_TOPIC=<Confidence response topic>

```
Note: Replace the endpoints with the actual endpoints

### Run the Server

`uvicorn src.main:app --reload`

### Run the examples

`python src/example.py`

### Run the Server

`uvicorn src.main:app --reload`

### Run Unit tests

####  Run Coverage
`python -m coverage run --source=src -m unittest discover -s tests/unit_tests`

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
    "confidence_level": "90.0",
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
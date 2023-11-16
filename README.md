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

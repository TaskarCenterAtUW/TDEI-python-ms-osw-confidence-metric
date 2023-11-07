import uuid
import asyncio
import datetime
from io import BytesIO, StringIO
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage

TOPIC = 'gtfs-flex-upload'
SUBSCRIPTION = 'uploadprocessor'
CONTAINER_NAME = 'tdei-storage-test'


def test_topics():
    print('\n\nTest Publish and receive messages')
    topic_object = Core.get_topic(topic_name=TOPIC)

    queue_message = QueueMessage.data_from({
        'message': str(uuid.uuid4().hex),
        'data': {'a': 1}
    })
    print(f'Message Published: {QueueMessage.to_dict(queue_message)}')
    topic_object.publish(data=queue_message)
    msg = topic_object.subscribe(subscription=SUBSCRIPTION)
    print(f'Received Message: {msg} \n')


def test_storage_upload():
    print('\n\nTesting Upload...')
    azure_client = Core.get_storage_client()
    container = azure_client.get_container(container_name=CONTAINER_NAME)
    # Creating a text stream
    txt = 'foo\nbar\nbaz'
    file_like_io = StringIO(txt)
    basename = 'sample-file'
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = '_'.join([basename, suffix])
    test_file = container.create_file(f'{filename}.txt', 'text/plain')
    print('Start uploading...')
    test_file.upload(file_like_io.read())
    print('Uploaded \n')


def test_storage():
    print('\n\nGetting All files from a container')
    azure_client = Core.get_storage_client()
    container = azure_client.get_container(container_name=CONTAINER_NAME)
    list_of_files = container.list_files()
    for file in list_of_files:
        print(file.name)
        print(file.mimetype)

    print('Got All the files from a container \n')


def test_logger():
    print('\n\nTesting Logger')
    logger = Core.get_logger()
    print('Sending Add Request Log')
    logger.add_request({
        'sample': 'text'
    })
    print('Sent Add Request Log \n')

    print('Sending Info Log')
    logger.info(message='Info Message')
    print('Sent Info Log \n')

    print('Sending Debug Log')
    logger.debug(message='Debug Message')
    print('Sent Debug Log \n')

    print('Sending Record Metric Log')
    logger.record_metric(name='ABC', value='XYZ')
    print('Sent Record Metric Log \n')


# def test_local_logger():
#     print('\n\nTesting Local Logger')
#     logger = Core.get_logger(provider='Local')
#     print('Sending Add Request Log Locally')
#     logger.add_request({
#         'sample': 'text'
#     })
#     print('Sent Add Request Log \n')
#
#     print('Sending Info Log Locally')
#     logger.info(message='Info Message')
#     print('Sent Info Log \n')
#
#     print('Sending Debug Log Locally')
#     logger.debug(message='Debug Message')
#     print('Sent Debug Log \n')
#
#     print('Sending Record Metric Log Locally')
#     logger.record_metric(name='ABC', value='XYZ')
#     print('Sent Record Metric Log \n')


if __name__ == "__main__":
    test_topics()
    test_storage_upload()
    test_storage()
    test_logger()
    # Make sure to run the server before running the local logger
    # test_local_logger()

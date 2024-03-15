import unittest
from src.models.confidence_request import ConfidenceRequest, RequestData


class TestConfidenceRequest(unittest.TestCase):

    def test_confidence_request_creation(self):
        # Test case for creating a ConfidenceRequest instance

        # Arrange
        req_body = RequestData(
            jobId='123',
            data_file='data.csv',
            meta_file='meta.json',
            trigger_type='manual'
        )

        # Act
        request_instance = ConfidenceRequest(
            messageId='123',
            messageType='123',
            data=req_body.__dict__
        )

        # Assert
        self.assertIsInstance(request_instance, ConfidenceRequest)
        self.assertEqual(request_instance.data.jobId, req_body.jobId)
        self.assertEqual(request_instance.data.data_file, req_body.data_file)
        self.assertEqual(request_instance.data.meta_file, req_body.meta_file)
        self.assertEqual(request_instance.data.trigger_type, req_body.trigger_type)

    def test_confidence_request_equality(self):
        # Test case for checking equality of ConfidenceRequest instances

        # Arrange
        req_body1 = RequestData(
            jobId='123',
            data_file='data.csv',
            meta_file='meta.json',
            trigger_type='manual'
        )
        req_body2 = RequestData(
            jobId='123',
            data_file='data.csv',
            meta_file='meta.json',
            trigger_type='manual'
        )
        req_body3 = RequestData(
            jobId='456',
            data_file='data.csv',
            meta_file='meta.json',
            trigger_type='manual'
        )

        request_instance_1 = ConfidenceRequest(messageId='MSG_1', messageType='MSG_TYPE_1', data=req_body1.__dict__)
        request_instance_2 = ConfidenceRequest(messageId='MSG_2', messageType='MSG_TYPE_2', data=req_body2.__dict__)
        request_instance_3 = ConfidenceRequest(messageId='MSG_3', messageType='MSG_TYPE_3', data=req_body3.__dict__)

        # Assert
        self.assertEqual(request_instance_1.data, request_instance_2.data)
        self.assertNotEqual(request_instance_1, request_instance_3)
        self.assertNotEqual(request_instance_2, request_instance_3)


if __name__ == '__main__':
    unittest.main()

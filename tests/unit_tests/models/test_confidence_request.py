import unittest
from src.models.confidence_request import ConfidenceRequest


class TestConfidenceRequest(unittest.TestCase):

    def test_confidence_request_creation(self):
        # Test case for creating a ConfidenceRequest instance

        # Arrange
        job_id = '123'
        data_file = 'data.csv'
        meta_file = 'meta.json'
        trigger_type = 'manual'

        # Act
        request_instance = ConfidenceRequest(
            jobId=job_id,
            data_file=data_file,
            meta_file=meta_file,
            trigger_type=trigger_type
        )

        # Assert
        self.assertIsInstance(request_instance, ConfidenceRequest)
        self.assertEqual(request_instance.jobId, job_id)
        self.assertEqual(request_instance.data_file, data_file)
        self.assertEqual(request_instance.meta_file, meta_file)
        self.assertEqual(request_instance.trigger_type, trigger_type)

    def test_confidence_request_equality(self):
        # Test case for checking equality of ConfidenceRequest instances

        # Arrange
        request_instance_1 = ConfidenceRequest('123', 'data.csv', 'meta.json', 'manual')
        request_instance_2 = ConfidenceRequest('123', 'data.csv', 'meta.json', 'manual')
        request_instance_3 = ConfidenceRequest('456', 'data.csv', 'meta.json', 'manual')

        # Assert
        self.assertEqual(request_instance_1, request_instance_2)
        self.assertNotEqual(request_instance_1, request_instance_3)
        self.assertNotEqual(request_instance_2, request_instance_3)


if __name__ == '__main__':
    unittest.main()

import unittest
from src.models.confidence_response import ConfidenceResponse


class TestConfidenceResponse(unittest.TestCase):

    def test_confidence_response_creation(self):
        # Test case for creating a ConfidenceResponse instance

        # Arrange
        job_id = '123'
        confidence_level = 0.75
        confidence_library_version = 'v1.0.0'
        status = 'success'
        message = 'Confidence calculation completed.'

        # Act
        response_instance = ConfidenceResponse(
            jobId=job_id,
            confidence_level=confidence_level,
            confidence_library_version=confidence_library_version,
            status=status,
            message=message
        )

        # Assert
        self.assertIsInstance(response_instance, ConfidenceResponse)
        self.assertEqual(response_instance.jobId, job_id)
        self.assertEqual(response_instance.confidence_level, confidence_level)
        self.assertEqual(response_instance.confidence_library_version, confidence_library_version)
        self.assertEqual(response_instance.status, status)
        self.assertEqual(response_instance.message, message)

    def test_confidence_response_equality(self):
        # Test case for checking equality of ConfidenceResponse instances

        # Arrange
        response_instance_1 = ConfidenceResponse('123', 0.75, 'v1.0.0', 'success', 'Message 1')
        response_instance_2 = ConfidenceResponse('123', 0.75, 'v1.0.0', 'success', 'Message 2')
        response_instance_3 = ConfidenceResponse('456', 0.85, 'v2.0.0', 'failure', 'Message 3')

        # Assert
        self.assertEqual(response_instance_1.jobId, response_instance_2.jobId)
        self.assertEqual(response_instance_1.confidence_level, response_instance_2.confidence_level)
        self.assertEqual(response_instance_1.confidence_library_version, response_instance_2.confidence_library_version)
        self.assertEqual(response_instance_1.status, response_instance_2.status)

        self.assertNotEqual(response_instance_1, response_instance_3)
        self.assertNotEqual(response_instance_2, response_instance_3)


if __name__ == '__main__':
    unittest.main()

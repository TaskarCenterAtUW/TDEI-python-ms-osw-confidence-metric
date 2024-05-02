import unittest
from src.models.confidence_response import ConfidenceResponse, ResponseData


class TestConfidenceResponse(unittest.TestCase):

    def test_confidence_response_creation(self):
        # Test case for creating a ConfidenceResponse instance

        # Arrange
        res_body = ResponseData(
            jobId='123',
            confidence_scores=0.75,
            confidence_library_version='v1.0.0',
            status='success',
            message='Confidence calculation completed.',
            success=True
        )

        # Act
        response_instance = ConfidenceResponse(
            messageId='id',
            messageType='type',
            data=res_body.__dict__
        )

        # Assert
        self.assertIsInstance(response_instance, ConfidenceResponse)
        self.assertEqual(response_instance.data.jobId, res_body.jobId)
        self.assertEqual(response_instance.data.confidence_scores, res_body.confidence_scores)
        self.assertEqual(response_instance.data.confidence_library_version, res_body.confidence_library_version)
        self.assertEqual(response_instance.data.status, res_body.status)
        self.assertEqual(response_instance.data.message, res_body.message)

    def test_confidence_response_equality(self):
        # Test case for checking equality of ConfidenceResponse instances

        # Arrange
        res_body1 = ResponseData(
            jobId='123',
            confidence_scores=0.75,
            confidence_library_version='v1.0.0',
            status='success',
            message='Message 1',
            success=True
        )

        res_body2 = ResponseData(
            jobId='123',
            confidence_scores=0.75,
            confidence_library_version='v1.0.0',
            status='success',
            message='Message 2',
            success=True
        )

        res_body3 = ResponseData(
            jobId='456',
            confidence_scores=0.85,
            confidence_library_version='v2.0.0',
            status='failure',
            message='Message 3',
            success=False
        )
        response_instance_1 = ConfidenceResponse(messageType='MSG_TYPE_1', messageId='MSG_1', data=res_body1.__dict__)
        response_instance_2 = ConfidenceResponse(messageType='MSG_TYPE_2', messageId='MSG_2', data=res_body2.__dict__)
        response_instance_3 = ConfidenceResponse(messageType='MSG_TYPE_3', messageId='MSG_3', data=res_body3.__dict__)


        # Assert
        self.assertEqual(response_instance_1.data.jobId, response_instance_2.data.jobId)
        self.assertEqual(response_instance_1.data.confidence_scores, response_instance_2.data.confidence_scores)
        self.assertEqual(response_instance_1.data.confidence_library_version, response_instance_2.data.confidence_library_version)
        self.assertEqual(response_instance_1.data.status, response_instance_2.data.status)

        self.assertNotEqual(response_instance_1, response_instance_3)
        self.assertNotEqual(response_instance_2, response_instance_3)


if __name__ == '__main__':
    unittest.main()

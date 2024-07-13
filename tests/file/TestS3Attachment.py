import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import boto3
from pywxdump.file.S3Attachment import S3Attachment


class TestS3Attachment(unittest.TestCase):

    @patch('boto3.client')
    def setUp(self, mock_client):
        self.mock_client = MagicMock()
        mock_client.return_value = self.mock_client
        s3_config = MagicMock()
        self.attachment = S3Attachment(s3_config)
        self.test_s3_url = "s3://test_bucket/test_file"
        self.test_s3_dir = "s3://test_bucket/test_folder/"

    @patch.object(S3Attachment, 'exists')
    @patch.object(S3Attachment, 'isFolder')
    @patch('boto3.client')
    def test_removal_of_existing_file(self, mock_client, mock_isFolder, mock_exists):
        mock_exists.return_value = True
        mock_isFolder.return_value = False
        mock_client.return_value = MagicMock()
        self.assertTrue(self.attachment.remove(self.test_s3_url))

    @patch.object(S3Attachment, 'exists')
    def test_removal_of_non_existing_file(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            self.attachment.remove(self.test_s3_url)

    @patch.object(S3Attachment, 'exists')
    @patch.object(S3Attachment, 'isFolder')
    def test_removal_of_folder_instead_of_file(self, mock_isFolder, mock_exists):
        mock_exists.return_value = True
        mock_isFolder.return_value = True
        with self.assertRaises(ValueError):
            self.attachment.remove(self.test_s3_url)

    @patch.object(S3Attachment, 'exists')
    @patch.object(S3Attachment, 'isdir')
    def test_removal_with_s3_error(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = False
        # 模拟 ClientError
        error_response = {'Error': {'Code': 'InvalidRequest', 'Message': 'Some error message'}}
        self.mock_client.delete_object.side_effect = ClientError(error_response, 'delete_object')
        with self.assertRaises(ClientError):
            self.attachment.remove(self.test_s3_url)

    @patch.object(S3Attachment, 'exists')
    def test_getsize_existing_file(self, mock_exists):
        mock_exists.return_value = True
        self.mock_client.head_object.return_value = {'ContentLength': 100}
        self.assertEqual(self.attachment.getsize(self.test_s3_url), 100)

    def test_getsize_non_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.attachment.getsize('non_existing_file')

    @patch.object(S3Attachment, 'isdir')
    def test_getsize_existing_folder(self, mock_isdir):
        mock_isdir.return_value = True
        self.mock_client.list_objects_v2.return_value = {'Contents': [{'Size': 100}, {'Size': 300}]}
        self.assertEqual(self.attachment.getsize(self.test_s3_dir), 400)


if __name__ == '__main__':
    unittest.main()

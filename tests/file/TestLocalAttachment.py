import os
import unittest
from unittest.mock import patch
from pywxdump.file.LocalAttachment import LocalAttachment
import tempfile


class TestLocalAttachment(unittest.TestCase):

    def setUp(self):
        self.attachment = LocalAttachment()
        self.test_file_path = self.attachment.join(tempfile.gettempdir(),"test.txt")
        self.test_dir_path = self.attachment.join(tempfile.gettempdir(),"test_dir")

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.test_dir_path):
            for dirpath, dirnames, filenames in os.walk(self.test_dir_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    os.remove(fp)
            os.rmdir(self.test_dir_path)

    def test_remove_existing_file(self):
        with open(self.test_file_path, 'w') as f:
            f.write("test")
        self.assertTrue(self.attachment.remove(self.test_file_path))
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_remove_non_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.attachment.remove(self.test_file_path)

    @patch('os.remove')
    def test_remove_os_error(self, mock_remove):
        mock_remove.side_effect = OSError
        with self.assertRaises(OSError):
            self.attachment.remove(self.test_file_path)

    def test_getsize_existing_file(self):
        # 清理测试环境
        self.tearDown()
        with open(self.test_file_path, "w") as f:
            f.write("Hello, World!")
        self.assertEqual(self.attachment.getsize(self.test_file_path), 13)

    def test_getsize_non_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.attachment.getsize('non_existing_file')

    def test_getsize_existing_folder(self):
        # 清理测试环境
        self.tearDown()
        os.mkdir(self.test_dir_path)
        with open(os.path.join(self.test_dir_path, "file1.txt"), "w") as f:
            f.write("Hello, World!")
        with open(os.path.join(self.test_dir_path, "file2.txt"), "w") as f:
            f.write("Hello, World!")
        self.assertEqual(self.attachment.getsize(self.test_dir_path), 26)

if __name__ == '__main__':
    unittest.main()

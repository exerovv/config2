import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from main import find_file_by_hash, get_commit_history, build_mermaid_graph, save_mermaid_file, generate_png_from_mermaid

class TestFindFileByHash(unittest.TestCase):
    @patch('os.walk')
    @patch('subprocess.run')
    def test_find_existing_file(self, mock_run, mock_walk):
        mock_walk.return_value = [(os.path.join('/repo'), ('subdir',), ('file.txt',))]
        mock_run.return_value.stdout = 'targethash\n'

        result = find_file_by_hash('/repo', 'targethash')
        self.assertEqual(result, os.path.join('/repo', 'file.txt'))

    @patch('os.walk')
    @patch('subprocess.run')
    def test_no_matching_hash(self, mock_run, mock_walk):
        mock_walk.return_value = [(os.path.join('/repo'), ('subdir',), ('file.txt',))]
        mock_run.return_value.stdout = 'differenthash\n'

        result = find_file_by_hash('/repo', 'targethash')
        self.assertIsNone(result)

    @patch('os.walk')
    @patch('subprocess.run')
    def test_multiple_files(self, mock_run, mock_walk):
        mock_walk.return_value = [(os.path.join('/repo'), ('subdir',), ('file1.txt', 'file2.txt'))]
        mock_run.side_effect = [MagicMock(stdout='wronghash\n'), MagicMock(stdout='targethash\n')]

        result = find_file_by_hash('/repo', 'targethash')
        self.assertEqual(result, os.path.join('/repo', 'file2.txt'))

if __name__ == '__main__':
    unittest.main()
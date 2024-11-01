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

class TestGetCommitHistory(unittest.TestCase):
    @patch('subprocess.run')
    def test_commit_history_retrieved(self, mock_run):
        mock_run.return_value.stdout = 'hash1 commit message 1\nhash2 commit message 2\n'
        commits = get_commit_history('/repo', 'file.txt')
        self.assertEqual(commits, ['hash1 commit message 1', 'hash2 commit message 2'])

    @patch('subprocess.run')
    def test_no_commits_found(self, mock_run):
        mock_run.return_value.stdout = ''
        commits = get_commit_history('/repo', 'file.txt')
        self.assertEqual(commits, [])

    @patch('subprocess.run')
    def test_encoding_issue_handling(self, mock_run):
        mock_run.return_value.stdout = 'hash1 commit message with special chars á\n'
        commits = get_commit_history('/repo', 'file.txt')
        self.assertEqual(commits, ['hash1 commit message with special chars á'])

class TestBuildMermaidGraph(unittest.TestCase):
    def test_single_commit(self):
        commits = ['hash1 Initial commit']
        graph = build_mermaid_graph(commits)
        expected_graph = 'graph TD\n    b6abca8 --> 0e4652d\n    d8159fb  --> c484e16'
        self.assertEqual(graph, expected_graph)

    def test_multiple_commits(self):
        generated_graph = 'graph TD\n    hash1["First commit"]\n    hash1 --> hash2\n    hash2["Second commit"]\n'
        expected_graph = 'graph TD\n    hash1["First commit"]\n    hash2["Second commit"]\n    hash1 --> hash2\n'

        self.assertEqual(set(generated_graph.splitlines()), set(expected_graph.splitlines()))

    def test_no_commits(self):
        graph = build_mermaid_graph([])
        self.assertEqual(graph, 'graph TD\n    b6abca8 --> 0e4652d\n    d8159fb  --> c484e16')

class TestSaveMermaidFile(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_save_file_content(self, mock_open_func):
        graph = 'graph TD\n    hash1["Initial commit"]\n'
        save_mermaid_file(graph, 'test.mmd')
        mock_open_func.assert_called_once_with('test.mmd', 'w', encoding="utf-8")
        mock_open_func().write.assert_called_once_with(graph)

    @patch('builtins.open', new_callable=mock_open)
    def test_empty_graph(self, mock_open_func):
        graph = ''
        save_mermaid_file(graph, 'test_empty.mmd')
        mock_open_func.assert_called_once_with('test_empty.mmd', 'w', encoding="utf-8")
        mock_open_func().write.assert_called_once_with(graph)

class TestGeneratePngFromMermaid(unittest.TestCase):
    @patch('subprocess.run')
    def test_successful_png_creation(self, mock_run):
        mock_run.return_value.returncode = 0
        generate_png_from_mermaid('test.mmd', 'output.png', 'mermaid-cli')
        mock_run.assert_called_once_with(['mermaid-cli', '-i', 'test.mmd', '-o', 'output.png'])

    @patch('subprocess.run', side_effect=Exception("PNG creation failed"))
    def test_png_creation_failure(self, mock_run):
        mermaid_tool_path = "/path/to/mermaid"
        with self.assertRaises(Exception) as context:
            generate_png_from_mermaid("test.mmd", "output.png", mermaid_tool_path)

        self.assertIn("PNG creation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()

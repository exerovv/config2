import subprocess
import os
import argparse
import re

def find_file_by_hash(repo_path, target_hash):
    for dirpath, _, filenames in os.walk(repo_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            cmd = ["powershell", "-Command", f"(Get-FileHash -Path '{file_path}' -Algorithm SHA256).Hash"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
            file_hash = result.stdout.strip()

            if file_hash == target_hash:
                return file_path
    return None

def get_commit_history(repo_path, file_path):
    cmd = ["git", "-C", repo_path, "log", "--all", "--pretty=format:%H %s", "--", file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    return result.stdout.strip().splitlines()

def build_mermaid_graph(commits):
    mermaid_graph = "graph TD\n"
    previous_commit = None
    for line in commits:
        match = re.match(r'(\w+)\s+(.*)', line)
        if match:
            commit_hash, message = match.groups()
            mermaid_graph += f'    {commit_hash}["{message}"]\n'
            if previous_commit:
                mermaid_graph += f'    {previous_commit} --> {commit_hash}\n'
            previous_commit = commit_hash
    return mermaid_graph

def main():
    parser = argparse.ArgumentParser(description="Commit Dependency Graph Visualizer")
    parser.add_argument('--viz', required=True, help='Path to the graph visualization program (Mermaid CLI)')
    parser.add_argument('--repo', required=True, help='Path to the git repository to analyze')
    parser.add_argument('--output', required=True, help='Path to save the graph image (without extension)')
    parser.add_argument('--file_hash', required=True, help='File hash to find in the repository')

    args = parser.parse_args()


    if not os.path.exists(args.viz):
        print(f"Visualization program {args.viz} not found.")
        return

    if not os.path.exists(args.repo):
        print(f"Repository {args.repo} not found.")
        return

    file_path = find_file_by_hash(args.repo, args.file_hash)
    if not file_path:
        print("File with the specified hash not found in the repository.")
        return

    commits = get_commit_history(args.repo, file_path)
    if not commits:
        print("No commits found for the specified file.")
        return

if __name__ == "__main__":
    main()
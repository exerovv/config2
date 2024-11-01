import subprocess
import os
import argparse

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
    cmd = ["git", "-C", repo_path, "log", "--pretty=format:%H %s %P", "--", file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8")

    commit_data = []
    for line in result.stdout.strip().split("\n"):
        message = []
        parents = []
        parts = line.split()
        commit = parts[0]
        for item in parts[1:]:
            if len(item) == 40 and all(c in '0123456789abcdef' for c in item):
                parents.append(item)
            else:
                message.append(item)
        commit_data.append((commit, parents, message))

    return commit_data

def build_mermaid_graph(commits):
    mermaid_graph = "graph TD\n"
    for commit in commits:
        mermaid_graph += f'    {commit[0]}["{' '.join(commit[2])}"]\n'
    for commit in commits:
        for par in commit[1]:
            mermaid_graph += f'    {commit[0]} --> {par}\n'
    return mermaid_graph

def save_mermaid_file(mermaid_graph, output_path):
    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(mermaid_graph)

def generate_png_from_mermaid(mermaid_path, output_image_path, mermaid_tool_path):
    cmd = [mermaid_tool_path, "-i", mermaid_path, "-o", output_image_path]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Ошибка при создании PNG из Mermaid файла.")
    else:
        print("Graph visualization created successfully.")

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

    mermaid_graph = build_mermaid_graph(commits)
    mermaid_file = "graph.mmd"
    save_mermaid_file(mermaid_graph, mermaid_file)

    output_image_path = f"{args.output}.png"
    generate_png_from_mermaid(mermaid_file, output_image_path, args.viz)

    # os.remove(mermaid_file)

if __name__ == "__main__":
    main()
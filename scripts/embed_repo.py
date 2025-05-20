#!/usr/bin/env python3
"""
Script to embed external repositories in the vendor directory.
Removes .git directories and adds metadata about the source.
"""
import os
import sys
import shutil
import subprocess
import json
import datetime
import tempfile

def main():
    if len(sys.argv) < 2:
        print("Usage: embed_repo.py REPO_URL [BRANCH]")
        return 1
    
    repo_url = sys.argv[1]
    branch = "main"
    if len(sys.argv) > 2:
        branch = sys.argv[2]
    
    # Extract repo name from URL
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    target_dir = os.path.join("vendor", repo_name)
    
    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository
        subprocess.run(["git", "clone", "--branch", branch, repo_url, temp_dir], check=True)
        
        # Get repo metadata
        current_dir = os.getcwd()
        os.chdir(temp_dir)
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        commit_date = subprocess.check_output(["git", "show", "-s", "--format=%ci", "HEAD"]).decode().strip()
        os.chdir(current_dir)
        
        # Create metadata
        metadata = {
            "source_url": repo_url,
            "commit_hash": commit_hash,
            "commit_date": commit_date,
            "embedded_date": datetime.datetime.now().isoformat(),
            "branch": branch
        }
        
        # Create vendor directory if needed
        os.makedirs("vendor", exist_ok=True)
        
        # Remove target directory if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Copy the repository without .git directory
        shutil.copytree(temp_dir, target_dir, ignore=lambda path, names: [".git"])
        
        # Write metadata file
        with open(os.path.join(target_dir, ".repo_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Repository {repo_name} embedded in {target_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
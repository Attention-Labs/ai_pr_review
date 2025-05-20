# Repository Embedding Tool

This repository contains a tool for embedding external repositories for offline use.

## Usage

```bash
python scripts/embed_repo.py https://github.com/username/repo [branch]
```

The repository will be embedded in the vendor/ directory with metadata intact.

## Features

- Clones repositories to a temporary directory
- Removes .git directories to avoid nested git issues
- Preserves metadata about the source repository
- Places files in the vendor/ directory
```

## Example

See the embedded [whatthepatch](https://github.com/cscorley/whatthepatch) repository in the vendor/ directory.
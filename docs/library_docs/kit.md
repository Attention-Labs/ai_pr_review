<file_map>
/Users/darin/docs/kit
├── api
│   ├── code_searcher.mdx
│   ├── dependency-analyzer.mdx
│   ├── docstring-indexer.mdx
│   ├── repository.mdx
│   ├── rest-api.mdx
│   ├── summarizer.mdx
│   └── summary-searcher.mdx
├── core-concepts
│   ├── code-summarization.mdx
│   ├── configuring-semantic-search.mdx
│   ├── context-assembly.mdx
│   ├── dependency-analysis.mdx
│   ├── docstring-indexing.mdx
│   ├── llm-context-best-practices.mdx
│   ├── repository-api.mdx
│   ├── search-approaches.mdx
│   ├── semantic-search.mdx
│   └── tool-calling-with-kit.mdx
├── development
│   ├── roadmap.mdx
│   └── running-tests.mdx
├── extending
│   └── adding-languages.mdx
├── introduction
│   ├── overview.mdx
│   ├── quickstart.mdx
│   └── usage-guide.mdx
├── mcp
│   └── using-kit-with-mcp.md
├── tutorials
│   ├── ai_pr_reviewer.mdx
│   ├── codebase_summarizer.mdx
│   ├── codebase-qa-bot.mdx
│   ├── dependency_graph_visualizer.mdx
│   ├── docstring_search.mdx
│   ├── dump_repo_map.mdx
│   ├── exploring-kit-interactively.mdx
│   ├── integrating_supersonic.mdx
│   └── recipes.mdx
├── index.mdx
├── README.mdx
└── recipes.mdx

</file_map>

<file_contents>
File: /Users/darin/docs/kit/api/code_searcher.mdx
```mdx
---
title: CodeSearcher API
---

import { Aside } from '@astrojs/starlight/components';

This page details the API for the `CodeSearcher` class, used for performing text and regular expression searches across your repository.

## Initialization

To use the `CodeSearcher`, you first need to initialize it with the path to your repository:

```python
from kit.code_searcher import CodeSearcher

searcher = CodeSearcher(repo_path="/path/to/your/repo")
# Or, if you have a kit.Repository object:
searcher = repo.get_code_searcher()
```

<Aside type="note">
  If you are using the `kit.Repository` object, you can obtain a `CodeSearcher` instance via `repo.get_code_searcher()` which comes pre-configured with the repository path.
</Aside>

## `SearchOptions` Dataclass

The `search_text` method uses a `SearchOptions` dataclass to control search behavior. You can import it from `kit.code_searcher`.

```python
from kit.code_searcher import SearchOptions
```

**Fields:**

*   `case_sensitive` (bool): 
    *   If `True` (default), the search query is case-sensitive.
    *   If `False`, the search is case-insensitive.
*   `context_lines_before` (int):
    *   The number of lines to include before each matching line. Defaults to `0`.
*   `context_lines_after` (int):
    *   The number of lines to include after each matching line. Defaults to `0`.
*   `use_gitignore` (bool):
    *   If `True` (default), files and directories listed in the repository's `.gitignore` file will be excluded from the search.
    *   If `False`, `.gitignore` rules are ignored.

## Methods

### `search_text(query: str, file_pattern: str = "*.py", options: Optional[SearchOptions] = None) -> List[Dict[str, Any]]`

Searches for a text pattern (which can be a regular expression) in files matching the `file_pattern`.

*   **Parameters:**
    *   `query` (str): The text pattern or regular expression to search for.
    *   `file_pattern` (str): A glob pattern specifying which files to search in. Defaults to `"*.py"` (all Python files).
    *   `options` (Optional[SearchOptions]): An instance of `SearchOptions` to customize search behavior. If `None`, default options are used.
*   **Returns:**
    *   `List[Dict[str, Any]]`: A list of dictionaries, where each dictionary represents a match and contains:
        *   `"file"` (str): The relative path to the file from the repository root.
        *   `"line_number"` (int): The 1-indexed line number where the match occurred.
        *   `"line"` (str): The content of the matching line (with trailing newline stripped).
        *   `"context_before"` (List[str]): A list of strings, each being a line of context before the match.
        *   `"context_after"` (List[str]): A list of strings, each being a line of context after the match.
*   **Raises:**
    *   The method includes basic error handling for file operations and will print an error message to the console if a specific file cannot be processed, then continue with other files.

**Example Usage:**

```python
from kit.code_searcher import CodeSearcher, SearchOptions

# Assuming 'searcher' is an initialized CodeSearcher instance

# Basic search for 'my_function' in Python files
results_basic = searcher.search_text("my_function")

# Case-insensitive search with 2 lines of context before and after
custom_options = SearchOptions(
    case_sensitive=False,
    context_lines_before=2,
    context_lines_after=2
)
results_with_options = searcher.search_text(
    query=r"my_variable\s*=\s*\d+", # Example regex query
    file_pattern="*.txt",
    options=custom_options
)

for match in results_with_options:
    print(f"Found in {match['file']} at line {match['line_number']}:")
    for before_line in match['context_before']:
        print(f"  {before_line}")
    print(f"> {match['line']}")
    for after_line in match['context_after']:
        print(f"  {after_line}")
    print("---")

```

File: /Users/darin/docs/kit/api/dependency-analyzer.mdx
```mdx
---
title: DependencyAnalyzer API
description: API documentation for the DependencyAnalyzer class and its language-specific implementations.
---

The `DependencyAnalyzer` class and its derivatives provide tools for analyzing dependencies between components in a codebase. These analyzers help you understand module relationships, detect circular dependencies, export dependency graphs, and generate visualization and LLM-friendly context about codebase architecture.

## Base Class

**Class: `DependencyAnalyzer`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

`DependencyAnalyzer` is an abstract base class that defines the common interface for all language-specific dependency analyzers. You typically don't instantiate this class directly; instead, use the factory method `Repository.get_dependency_analyzer(language)` to get the appropriate analyzer for your target language.

```python
from kit import Repository

repo = Repository("/path/to/your/codebase")
analyzer = repo.get_dependency_analyzer('python')  # or 'terraform'
```

### Constructor

```python
DependencyAnalyzer(repository: Repository)
```

**Parameters:**

* **`repository`** (`Repository`, required):  
  A Kit `Repository` instance that provides access to the codebase.

### Methods

#### `build_dependency_graph`

**Method: `DependencyAnalyzer.build_dependency_graph`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Analyzes the entire repository and builds a dependency graph.

```python
graph = analyzer.build_dependency_graph()
```

**Returns:**

* A dictionary representing the dependency graph where:
  * Keys are component identifiers (e.g., module names for Python, resource IDs for Terraform)
  * Values are dictionaries containing component metadata and dependencies

#### `export_dependency_graph`

**Method: `DependencyAnalyzer.export_dependency_graph`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Exports the dependency graph to various formats.

```python
# Export to JSON file
result = analyzer.export_dependency_graph(
    output_format="json", 
    output_path="dependencies.json"
)

# Export to DOT file (for Graphviz)
result = analyzer.export_dependency_graph(
    output_format="dot", 
    output_path="dependencies.dot"
)

# Export to GraphML file (for tools like Gephi or yEd)
result = analyzer.export_dependency_graph(
    output_format="graphml", 
    output_path="dependencies.graphml"
)
```

**Parameters:**

* **`output_format`** (`str`, optional):  
  Format to export. One of: `"json"`, `"dot"`, `"graphml"`. Defaults to `"json"`.
* **`output_path`** (`str`, optional):  
  Path to save the output file. If `None`, returns the formatted data as a string.

**Returns:**

* If `output_path` is provided: Path to the output file
* If `output_path` is `None`: Formatted dependency data as a string

#### `find_cycles`

**Method: `DependencyAnalyzer.find_cycles`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Finds cycles (circular dependencies) in the dependency graph.

```python
cycles = analyzer.find_cycles()
if cycles:
    print(f"Found {len(cycles)} circular dependencies:")
    for cycle in cycles:
        print(f"  {' → '.join(cycle)} → {cycle[0]}")
```

**Returns:**

* A list of cycles, where each cycle is a list of component identifiers

#### `visualize_dependencies`

**Method: `DependencyAnalyzer.visualize_dependencies`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Generates a visualization of the dependency graph.

```python
# Generate a PNG visualization
viz_file = analyzer.visualize_dependencies(
    output_path="dependency_graph", 
    format="png"
)
```

**Parameters:**

* **`output_path`** (`str`, required):  
  Path to save the visualization (without extension).
* **`format`** (`str`, optional):  
  Output format. One of: `"png"`, `"svg"`, `"pdf"`. Defaults to `"png"`.

**Returns:**

* Path to the generated visualization file

#### `generate_llm_context`

**Method: `DependencyAnalyzer.generate_llm_context`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Generates a concise, natural language description of the dependency graph optimized for LLM consumption.

```python
# Generate markdown context
context = analyzer.generate_llm_context(
    max_tokens=4000,
    output_format="markdown",
    output_path="dependency_context.md"
)

# Or generate plain text context
context = analyzer.generate_llm_context(
    max_tokens=4000,
    output_format="text",
    output_path="dependency_context.txt"
)
```

**Parameters:**

* **`max_tokens`** (`int`, optional):  
  Approximate maximum number of tokens in the output (rough guideline). Defaults to 4000.
* **`output_format`** (`str`, optional):  
  Format of the output. One of: `"markdown"`, `"text"`. Defaults to `"markdown"`.
* **`output_path`** (`str`, optional):  
  Path to save the output to a file. If `None`, returns the formatted string.

**Returns:**

* A string containing the natural language description of the dependency structure

#### Factory Method: `get_for_language`

**Method: `DependencyAnalyzer.get_for_language`**  
*(defined in `kit/dependency_analyzer/dependency_analyzer.py`)*

Factory method to get an appropriate `DependencyAnalyzer` for the specified language. This is typically used internally by the `Repository.get_dependency_analyzer` method.

```python
analyzer = DependencyAnalyzer.get_for_language(repository, "python")
```

**Parameters:**

* **`repository`** (`Repository`, required):  
  A Kit `Repository` instance.
* **`language`** (`str`, required):  
  Language identifier (e.g., `"python"`, `"terraform"`).

**Returns:**

* An appropriate `DependencyAnalyzer` instance for the language

## Language-Specific Implementations

### PythonDependencyAnalyzer

**Class: `PythonDependencyAnalyzer`**  
*(defined in `kit/dependency_analyzer/python_dependency_analyzer.py`)*

The `PythonDependencyAnalyzer` extends the base `DependencyAnalyzer` to analyze Python codebases, focusing on import relationships between modules.

#### Additional Methods

##### `get_module_dependencies`

**Method: `PythonDependencyAnalyzer.get_module_dependencies`**  
*(defined in `kit/dependency_analyzer/python_dependency_analyzer.py`)*

Gets dependencies for a specific Python module.

```python
# Get direct dependencies
deps = python_analyzer.get_module_dependencies("my_package.my_module")

# Get all dependencies (including indirect)
all_deps = python_analyzer.get_module_dependencies(
    "my_package.my_module", 
    include_indirect=True
)
```

**Parameters:**

* **`module_name`** (`str`, required):  
  Name of the module to check.
* **`include_indirect`** (`bool`, optional):  
  Whether to include indirect dependencies. Defaults to `False`.

**Returns:**

* List of module names this module depends on

##### `get_file_dependencies`

**Method: `PythonDependencyAnalyzer.get_file_dependencies`**  
*(defined in `kit/dependency_analyzer/python_dependency_analyzer.py`)*

Gets detailed dependency information for a specific file.

```python
file_deps = python_analyzer.get_file_dependencies("path/to/file.py")
```

**Parameters:**

* **`file_path`** (`str`, required):  
  Path to the file to analyze.

**Returns:**

* Dictionary with dependency information for the file

##### `generate_dependency_report`

**Method: `PythonDependencyAnalyzer.generate_dependency_report`**  
*(defined in `kit/dependency_analyzer/python_dependency_analyzer.py`)*

Generates a comprehensive dependency report for the repository.

```python
report = python_analyzer.generate_dependency_report(
    output_path="dependency_report.json"
)
```

**Parameters:**

* **`output_path`** (`str`, optional):  
  Path to save the report JSON. If `None`, returns the report data without saving.

**Returns:**

* Dictionary with the complete dependency report

### TerraformDependencyAnalyzer

**Class: `TerraformDependencyAnalyzer`**  
*(defined in `kit/dependency_analyzer/terraform_dependency_analyzer.py`)*

The `TerraformDependencyAnalyzer` extends the base `DependencyAnalyzer` to analyze Terraform (HCL) codebases, focusing on relationships between infrastructure resources, modules, variables, and other Terraform components.

#### Additional Methods

##### `get_resource_dependencies`

**Method: `TerraformDependencyAnalyzer.get_resource_dependencies`**  
*(defined in `kit/dependency_analyzer/terraform_dependency_analyzer.py`)*

Gets dependencies for a specific Terraform resource.

```python
# Get direct dependencies
deps = terraform_analyzer.get_resource_dependencies("aws_s3_bucket.example")

# Get all dependencies (including indirect)
all_deps = terraform_analyzer.get_resource_dependencies(
    "aws_s3_bucket.example", 
    include_indirect=True
)
```

**Parameters:**

* **`resource_id`** (`str`, required):  
  ID of the resource to check (e.g., `"aws_s3_bucket.example"`).
* **`include_indirect`** (`bool`, optional):  
  Whether to include indirect dependencies. Defaults to `False`.

**Returns:**

* List of resource IDs this resource depends on

##### `get_resource_by_type`

**Method: `TerraformDependencyAnalyzer.get_resource_by_type`**  
*(defined in `kit/dependency_analyzer/terraform_dependency_analyzer.py`)*

Finds all resources of a specific type.

```python
# Find all S3 buckets
s3_buckets = terraform_analyzer.get_resource_by_type("aws_s3_bucket")
```

**Parameters:**

* **`resource_type`** (`str`, required):  
  Type of resource to find (e.g., `"aws_s3_bucket"`).

**Returns:**

* List of resource IDs matching the specified type

##### `generate_resource_documentation`

**Method: `TerraformDependencyAnalyzer.generate_resource_documentation`**  
*(defined in `kit/dependency_analyzer/terraform_dependency_analyzer.py`)*

Generates documentation for Terraform resources in the codebase.

```python
docs = terraform_analyzer.generate_resource_documentation(
    output_path="terraform_resources.md"
)
```

**Parameters:**

* **`output_path`** (`str`, optional):  
  Path to save the documentation. If `None`, returns the documentation string.

**Returns:**

* String containing the markdown documentation of resources

## Key Features and Notes

- All dependency analyzers store absolute file paths for resources, making it easy to locate components in complex codebases with files that might have the same name in different directories.

- The `generate_llm_context` method produces summaries specially formatted for use as context with LLMs, focusing on the most significant patterns and keeping the token count manageable.

- Visualizations require the Graphviz software to be installed on your system.

- The dependency graph is built on first use and cached. If the codebase changes, you may need to call `build_dependency_graph()` again to refresh the analysis.

```

File: /Users/darin/docs/kit/api/summarizer.mdx
```mdx
---
title: Summarizer API
---

import { Aside } from '@astrojs/starlight/components';

This page details the API for the `Summarizer` class, used for interacting with LLMs for code summarization tasks.

## Initialization

Details on how to initialize the `Summarizer` (likely via `repo.get_summarizer()`).

<Aside type="note">
  Typically, you obtain a `Summarizer` instance via `repo.get_summarizer()` rather than initializing it directly.
</Aside>

## Methods

### `summarize_file(file_path: str) -> str`

Summarizes the content of the specified file.

*   **Parameters:**
    *   `file_path` (str): The path to the file within the repository.
*   **Returns:**
    *   `str`: The summary generated by the LLM.
*   **Raises:**
    *   `FileNotFoundError`: If the `file_path` does not exist in the repo.
    *   `LLMError`: If there's an issue communicating with the LLM.


### `summarize_function(file_path: str, function_name: str) -> str`

Summarizes a specific function within the specified file.

*   **Parameters:**
    *   `file_path` (str): The path to the file containing the function.
    *   `function_name` (str): The name of the function to summarize.
*   **Returns:**
    *   `str`: The summary generated by the LLM.
*   **Raises:**
    *   `FileNotFoundError`: If the `file_path` does not exist in the repo.
    *   `SymbolNotFoundError`: If the function cannot be found in the file.
    *   `LLMError`: If there's an issue communicating with the LLM.

### `summarize_class(file_path: str, class_name: str) -> str`

Summarizes a specific class within the specified file.

*   **Parameters:**
    *   `file_path` (str): The path to the file containing the class.
    *   `class_name` (str): The name of the class to summarize.
*   **Returns:**
    *   `str`: The summary generated by the LLM.
*   **Raises:**
    *   `FileNotFoundError`: If the `file_path` does not exist in the repo.
    *   `SymbolNotFoundError`: If the class cannot be found in the file.
    *   `LLMError`: If there's an issue communicating with the LLM.

## Configuration

Details on the configuration options (`OpenAIConfig`, etc.).
This is typically handled when calling `repo.get_summarizer(config=...)` or via environment variables read by the default `OpenAIConfig`.

The `Summarizer` currently uses `OpenAIConfig` for its LLM settings. When a `Summarizer` is initialized without a specific config object, it creates a default `OpenAIConfig` with the following parameters:

*   `api_key` (str, optional): Your OpenAI API key. Defaults to the `OPENAI_API_KEY` environment variable. If not found, an error will be raised.
*   `model` (str): The OpenAI model to use. Defaults to `"gpt-4o"`.
*   `temperature` (float): Sampling temperature for the LLM. Defaults to `0.7`.
*   `max_tokens` (int): The maximum number of tokens to generate in the summary. Defaults to `1000`.

You can customize this by creating an `OpenAIConfig` instance and passing it to `repo.get_summarizer()`:

```python
from kit.summaries import OpenAIConfig

# Example: Customize model and temperature
my_config = OpenAIConfig(model="o3-mini", temperature=0.2)
summarizer = repo.get_summarizer(config=my_config)

# Now summarizer will use o3-mini with temperature 0.2
summary = summarizer.summarize_file("path/to/your/file.py")
```

```

File: /Users/darin/docs/kit/api/rest-api.mdx
```mdx
---
title: Kit REST API
subtitle: HTTP endpoints for code intelligence operations
---

`kit` ships a lightweight FastAPI server that exposes most of the same
capabilities as the Python API and the MCP server, but over good old HTTP.
This page lists every route, its query-parameters and example `curl` invocations.

The server lives in `kit.api.app`.  Run it directly with:

```bash
uvicorn kit.api.app:app --reload
```

---
## 1  Opening a repository

```http
POST /repository
```
Body (JSON):
| field       | type   | required | description                      |
|-------------|--------|----------|----------------------------------|
| path_or_url | string | yes      | Local path **or** Git URL        |
| ref         | string | no       | Commit SHA / branch / tag        |
| github_token| string | no       | OAuth token for private clones   |

Return → `{ "id": "8b1d4f29c7b1" }`

The ID is deterministic: `sha1(<canonical-path>@<ref>)[:12]`.  Re-POSTing the
same path+ref always returns the same ID – so clients can cache it.

> Note If `path_or_url` is a **GitHub URL**, the server shells out to `git clone`.  Pass `github_token` to authenticate when cloning **private** repositories.

## 2  Navigation

| Method & path                                   | Purpose                    |
|-------------------------------------------------|----------------------------|
| `GET /repository/{id}/file-tree`                | JSON list of files/dirs    |
| `GET /repository/{id}/files/{path}`             | Raw text response          |
| `DELETE /repository/{id}`                       | Evict from registry/LRU    |

Example:
```bash
curl "$KIT_URL/repository/$ID/files/models/user.py"
```

## 3  Search

```http
GET /repository/{id}/search?q=<regex>&pattern=*.py
```
Returns grep-style hits with file & line numbers.

## 4  Symbols & usages

```http
GET /repository/{id}/symbols?file_path=...&symbol_type=function
GET /repository/{id}/usages?symbol_name=foo&symbol_type=function
```
`/symbols` without `file_path` scans the whole repo (cached).

## 5  Composite index

```http
GET /repository/{id}/index
```
Response:
```json
{
  "files": [ ... file-tree items ... ],
  "symbols": { "path/to/file.py": [ {"name": "foo", ...} ] }
}
```

## 6  Advanced Capabilities

These endpoints are included in the standard `kit` installation but may have specific runtime requirements:

| Route              | Key Runtime Requirement(s)                                    | Notes                                                                 |
|--------------------|---------------------------------------------------------------|-----------------------------------------------------------------------|
| `/summary`         | LLM API key (e.g., `OPENAI_API_KEY` in environment)           | Generates code summaries. Returns `400` if key is missing/invalid, `503` if LLM service fails. |
| `/dependencies`    | None for fetching graph data (Python/Terraform)               | Returns dependency graph. `graphviz` needed only for local visualization helpers, not this endpoint. |

### Upcoming Features

The following features are currently in development and will be added in future releases:

| Planned Feature | Description | Status |
|-----------------|-------------|--------|
| `/semantic-search` | Embedding-based search using vector databases to find semantically similar code chunks | Coming soon |
| Enhanced symbol analysis | Improved cross-language symbol detection and relationship mapping | Planned |

## 7  Common HTTP Status Codes

*   `200 OK`: Request succeeded.
*   `201 Created`: Repository opened successfully.
*   `204 No Content`: Repository deleted successfully.
*   `400 Bad Request`: Invalid parameters in the request (e.g., unsupported language for dependencies, missing API key for summaries).
*   `404 Not Found`: Requested resource (repository, file, symbol) could not be found.
*   `500 Internal Server Error`: An unexpected error occurred on the server.
*   `503 Service Unavailable`: An external service required by the handler (e.g., an LLM API) failed or is unavailable.

---
### Example session

```bash
# 1 Open local repo (deterministic id)
ID=$(curl -sX POST localhost:8000/repository \
     -d '{"path_or_url": "/my/project"}' \
     -H 'Content-Type: application/json' | jq -r .id)

# 2 Find every file that mentions "KeyError"
curl "localhost:8000/repository/$ID/search?q=KeyError"

# 3 Show snippet
curl "localhost:8000/repository/$ID/files/auth/session.py" | sed -n '80,95p'
``` 
```

File: /Users/darin/docs/kit/core-concepts/code-summarization.mdx
```mdx
---
title: Code Summarization
---

import { Aside } from '@astrojs/starlight/components';

In addition to the non-LLM based functions of the `Repository` class, 
`kit` also integrates directly with LLMs via the `Summarizer` class to provide intelligent code summarization capabilities. This helps you quickly understand the purpose and functionality of entire code files, specific functions, or classes.

## Getting Started

To use code summarization, you'll need an LLM provider configured. Currently, OpenAI, Anthropic, and Google Cloud's Generative AI models are supported.

1.  **Install Dependencies:**
    ```bash
    # Ensure you are in your project's virtual environment
    uv pip install cased-kit
    ```
    The installation includes all dependencies for OpenAI, Anthropic, and Google Cloud's Generative AI models.

2.  **Set API Key(s):** Configure the API key(s) for your chosen provider(s) as environment variables:
    ```bash
    # For OpenAI
    export OPENAI_API_KEY="sk-..."
    
    # For Anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    
    # For Google
    export GOOGLE_API_KEY="AIzaSy..."
    ```
    You only need to set the key for the provider(s) you intend to use. If no specific configuration is provided to the `Summarizer` (see 'Configuration (Advanced)' below), `kit` defaults to using OpenAI via `OpenAIConfig()`, which expects `OPENAI_API_KEY`.

    For `OpenAIConfig`, you can also customize parameters such as the `model`, `temperature`, or `base_url` (e.g., for connecting to services like OpenRouter). See the 'Configuration (Advanced)' section for detailed examples.

## Basic Usage: Summarizing Files

The primary way to access summarization is through the `Repository` object's `get_summarizer()` factory method.

```python
import kit
import os

# Ensure API key is set (replace with your actual key handling)
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY" 

try:
    # Load the repository
    repo = kit.Repository("/path/to/your/project")

    # Get the summarizer instance (defaults to OpenAIConfig using env var OPENAI_API_KEY)
    # See 'Configuration (Advanced)' for using Anthropic or Google.
    summarizer = repo.get_summarizer()

    # Summarize a specific file
    file_path = "src/main_logic.py"
    summary = summarizer.summarize_file(file_path)

    print(f"Summary for {file_path}:\n{summary}")

except Exception as e:
    print(f"An error occurred with the LLM provider: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

```

<Aside type="note">
  When you call `repo.get_summarizer()` (or instantiate `Summarizer` directly), it will use the appropriate LLM library based on the specified configuration (e.g., `openai`, `anthropic`, `google.genai`). All necessary libraries are included in the standard installation.
</Aside>

### How it Works

When you call `summarize_file`, `kit` performs the following steps:

1.  Retrieves the content of the specified file using `repo.get_file_content()`.
2.  Constructs a prompt containing the file content, tailored for code summarization.
3.  Sends the prompt to the configured LLM provider and model (e.g., OpenAI's GPT-4o).
4.  Parses the response and returns the summary text.

### Configuration (Advanced)

While environment variables are the default, you can provide specific configuration:

```python
from kit.summaries import OpenAIConfig, AnthropicConfig, GoogleConfig

# Load repo
repo = kit.Repository("/path/to/your/project")

# Define custom OpenAI configuration
openai_custom_config = OpenAIConfig(
    api_key="sk-...", # Can be omitted if OPENAI_API_KEY is set
    model="gpt-4o-mini"
)
# Get summarizer with specific OpenAI config
openai_summarizer = repo.get_summarizer(config=openai_custom_config)
# Summarize using the custom OpenAI configuration
openai_summary = openai_summarizer.summarize_file("src/utils_openai.py")
print(f"OpenAI Summary:\n{openai_summary}")
```

#### Using OpenAI-Compatible Endpoints (e.g., OpenRouter)

The `OpenAIConfig` also supports a `base_url` parameter, allowing you to use any OpenAI-compatible API endpoint, such as [OpenRouter](https://openrouter.ai/). This is useful for accessing a wide variety of models through a single API key and endpoint.

To use OpenRouter:
1. Your `api_key` in `OpenAIConfig` should be your OpenRouter API key.
2. Set the `base_url` to OpenRouter's API endpoint (e.g., `https://openrouter.ai/api/v1`).
3. The `model` parameter should be the specific model string as recognized by OpenRouter (e.g., `meta-llama/llama-3.3-70b-instruct`).

```
# Example for OpenRouter
openrouter_config = OpenAIConfig(
    api_key="YOUR_OPENROUTER_API_KEY", # Replace with your OpenRouter key
    model="meta-llama/llama-3.3-70b-instruct", # Example model on OpenRouter
    base_url="https://openrouter.ai/api/v1"
)

openrouter_summarizer = repo.get_summarizer(config=openrouter_config)
```

#### Additional Configs

# Define custom Anthropic configuration
anthropic_config = AnthropicConfig(
    api_key="sk-ant-...", # Can be omitted if ANTHROPIC_API_KEY is set
    model="claude-3-haiku-20240307"
)

# Define custom Google configuration
google_config = GoogleConfig(
    api_key="AIzaSy...", # Can be omitted if GOOGLE_API_KEY is set
    model="gemini-1.5-flash-latest"
)

```

## Advanced Usage

### Summarizing Functions and Classes

Beyond entire files, you can target specific functions or classes:

```python
import kit

repo = kit.Repository("/path/to/your/project")
summarizer = repo.get_summarizer() # Assumes OPENAI_API_KEY is set

# Summarize a specific function
function_summary = summarizer.summarize_function(
    file_path="src/core/processing.py", 
    function_name="process_main_data"
)
print(f"Function Summary:\n{function_summary}")

# Summarize a specific class
class_summary = summarizer.summarize_class(
    file_path="src/models/user.py",
    class_name="UserProfile"
)
print(f"Class Summary:\n{class_summary}")

```

<Aside type="note">
  Under the hood, `summarize_function` and `summarize_class` will use `kit`'s symbol extraction capabilities (`repo.extract_symbols`) to locate the precise code snippet for the target function or class before sending it to the LLM, providing more focused summaries.
</Aside>

### Combining with Other Repository Features

You can combine the `Summarizer` with other `Repository` methods for powerful workflows. For example, find all classes in a file and then summarize each one:

```python
import kit

repo = kit.Repository("/path/to/your/project")
summarizer = repo.get_summarizer()

file_to_analyze = "src/services/notification_service.py"

# 1. Find all symbols in the file
symbols = repo.extract_symbols(file_path=file_to_analyze)

# 2. Filter for classes
class_symbols = [s for s in symbols if s.get('type') == 'class']

# 3. Summarize each class
for sym in class_symbols:
    class_name = sym.get('name')
    if class_name:
        print(f"--- Summarizing Class: {class_name} ---")
        try:
            summary = summarizer.summarize_class(
                file_path=file_to_analyze, 
                class_name=class_name
            )
            print(summary)
        except Exception as e:
            print(f"Could not summarize {class_name}: {e}")
    print("\n")

```

<Aside type="note">
  While `repo.get_summarizer()` is the most convenient way to get a configured `Summarizer`, you can also instantiate it directly if needed:

  ```python
  from kit import Repository
  from kit.summaries import Summarizer, OpenAIConfig, AnthropicConfig, GoogleConfig

  my_repo = Repository("/path/to/code")
  
  # Example with AnthropicConfig
  # Similar approach for OpenAIConfig or GoogleConfig
  my_anthropic_config = AnthropicConfig(
      api_key="sk-ant-your-key", 
      model="claude-3-sonnet-20240229"
  )
  direct_summarizer = Summarizer(repo=my_repo, config=my_anthropic_config)
  
  # Or for OpenAI:
  # my_openai_config = OpenAIConfig(api_key="sk-your-key", model="gpt-4o")
  # direct_summarizer = Summarizer(repo=my_repo, config=my_openai_config)
  
  # Or for Google:
  # my_google_config = GoogleConfig(api_key="AIzaSy-your-key", model="gemini-pro")
  # direct_summarizer = Summarizer(repo=my_repo, config=my_google_config)

  summary = direct_summarizer.summarize_file("some/file.py")
  print(summary)
  ```
</Aside>

```

File: /Users/darin/docs/kit/core-concepts/configuring-semantic-search.mdx
```mdx
---
title: Configuring Semantic Search
---

Semantic search allows you to find code based on meaning rather than just keywords. To enable this in `kit`, you need to configure a vector embedding model and potentially a vector database backend.

## Required: Embedding Function

You must provide an embedding function (`embed_fn`) when first accessing semantic search features via `repo.get_vector_searcher()` or `repo.search_semantic()`.

This function takes a list of text strings and returns a list of corresponding embedding vectors.

```python
from kit import Repo
# Example using a hypothetical embedding function
from my_embedding_library import get_embeddings

repo = Repo("/path/to/repo")

# Define the embedding function wrapper if necessary
def embed_fn(texts: list[str]) -> list[list[float]]:
    # Adapt this to your specific embedding library/API
    return get_embeddings(texts)

# Pass the function when searching
results = repo.search_semantic("database connection logic", embed_fn=embed_fn)

# Or when getting the searcher explicitly
vector_searcher = repo.get_vector_searcher(embed_fn=embed_fn)
```

Popular choices include models from OpenAI, Cohere, or open-source models via libraries like Hugging Face's `sentence-transformers`.

## Backend Configuration

`kit`'s `VectorSearcher` uses a pluggable backend system for storing and querying vector embeddings. Currently, the primary supported and default backend is **ChromaDB**.

### ChromaDB (Default)

When you initialize `VectorSearcher` (typically via `repo.get_vector_searcher()`) without specifying a `backend` argument, `kit` automatically uses an instance of `ChromaDBBackend`.

**Configuration Options:**

*   **`persist_dir` (Optional[str]):** This is the most important configuration option. It specifies the directory where the ChromaDB index will be stored on disk. 
    *   If you provide a path to `repo.get_vector_searcher(persist_dir=...)` or directly to the `VectorSearcher` constructor, that path will be used.
    *   If no `persist_dir` is specified, `kit` defaults to creating the index in a subdirectory within your repository, typically at `YOUR_REPO_PATH/.kit/vector_db/`.
    *   Persisting the index allows you to reuse it across sessions without needing to re-embed and re-index your codebase every time.

At present, other ChromaDB-specific configurations (like collection names or distance metrics) are managed internally by `kit` with default settings. Future versions may expose more fine-grained control.

```python
# Example: Initialize with default ChromaDB backend and specify a persist directory
vector_searcher = repo.get_vector_searcher(
    embed_fn=my_embedding_function, 
    persist_dir="./my_custom_kit_vector_index" # Index will be saved here
)

# Building the index (first time or to update)
vector_searcher.build_index()

# Later, to reuse the persisted index:
# Ensure you use the same embed_fn and persist_dir
vector_searcher_reloaded = repo.get_vector_searcher(
    embed_fn=my_embedding_function, 
    persist_dir="./my_custom_kit_vector_index"
)
results = vector_searcher_reloaded.search("my query")
```

### Other Backends

While the `VectorDBBackend` interface is designed to support other vector databases, ChromaDB is the primary focus for now. If you have a need for other backends like Faiss (especially for purely in-memory, non-persisted use cases) or others, please raise an issue on the `kit` GitHub repository.

## Choosing an Embedding Model

Popular choices include models from OpenAI, Cohere, or open-source models via libraries like Hugging Face's `sentence-transformers`.

```

File: /Users/darin/docs/kit/core-concepts/context-assembly.mdx
```mdx
---
title: Assembling Context
---

When you send code to an LLM you usually **don’t** want the entire repository –
just the *most relevant* bits.  `ContextAssembler` helps you stitch those bits
together into a single prompt-sized string.

## Why you need it

* **Token limits** – GPT-4o tops out at ~128k tokens; some models less.
* **Signal-to-noise** – Cut boilerplate, focus the model on what matters.
* **Automatic truncation** – Keeps prompts within your chosen character budget.

## Quick start

```python
from kit import Repository, ContextAssembler

repo = Repository("/path/to/project")

# Assume you already have chunks, e.g. from repo.search_semantic()
chunks = repo.search_text("jwt decode")

assembler = ContextAssembler(max_chars=12_000)
context = assembler.from_chunks(chunks)

print(context)  # → Ready to drop into your chat prompt
```

`chunks` can be any list of dicts that include a `code` key – the helper trims
and orders them by length until the budget is filled.

### Fine-tuning

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_chars` | `12000` | Rough character cap for the final string. |
| `separator` | `"\n\n---\n\n"` | Separator inserted between chunks. |
| `header` / `footer` | `""` | Optional strings prepended/appended. |

```python
assembler = ContextAssembler(
    max_chars=8000,
    header="### Code context\n",
    footer="\n### End context",
)
```

## Combining with other tools

1. **Vector search → assemble → chat**
   ```python
   chunks = repo.search_semantic("retry backoff", embed_fn, top_k=10)
   prompt = assembler.from_chunks(chunks)
   response = my_llm.chat(prompt + "\n\nQ: …")
   ```
2. **Docstring search first** – Use `SummarySearcher` for high-level matches,
   then pull full code for those files via `repo.context`.  
3. **Diff review bots** – Feed only the changed lines + surrounding context.

## API reference

```python
from kit.llm_context import ContextAssembler
```

### `__init__(repo, *, title=None)`

Constructs a new `ContextAssembler`.

*   `repo`: A `kit.repository.Repository` instance.
*   `title` (optional): A string to prepend to the assembled context.

### `from_chunks(chunks, max_chars=12000, separator="...", header="", footer="")`

This is the primary method for assembling context from a list of code chunks.

*   `chunks`: A list of dictionaries, each with a `"code"` key.
*   `max_chars`: Target maximum character length for the output string.
*   `separator`: String to insert between chunks.
*   `header` / `footer`: Optional strings to wrap the entire context.

Returns a single string with concatenated, truncated chunks.

### Other methods

While `from_chunks` is the most common entry point, `ContextAssembler` also offers methods to add specific types of context if you're building a prompt manually:

*   `add_diff(diff_text)`: Adds a Git diff.
*   `add_file(file_path, highlight_changes=False)`: Adds the full content of a file.
*   `add_symbol_dependencies(file_path, max_depth=1)`: Adds content of files that `file_path` depends on.
*   `add_search_results(results, query)`: Formats and adds semantic search results.
*   `format_context()`: Returns the accumulated context as a string.

```

File: /Users/darin/docs/kit/core-concepts/docstring-indexing.mdx
```mdx
---
title: Docstring-based Vector Indexing
---
import { Steps, Aside } from '@astrojs/starlight/components';

<Aside type="note" title="Alpha Feature">
  The features described on this page, particularly symbol-level indexing and LLM-generated summaries, are currently in **alpha**. API and behavior may change in future releases. Please use with this in mind and report any issues or feedback.
</Aside>

<br />

`DocstringIndexer` builds a vector index using **LLM-generated summaries** of
source files ("docstrings") instead of the raw code.  This often yields more
relevant results because the embedded text focuses on *intent* rather than
syntax or specific variable names.

## Why use it?

* **Cleaner embeddings** – Comments like *“Summary of retry logic”* embed better
  than nested `for`-loops.
* **Smaller index** – One summary per file (or symbol) is < 1 kB, while the file
  itself might be thousands of tokens.
* **Provider-agnostic** – Works with any LLM supported by `kit.Summarizer`
  (OpenAI, Anthropic, Google…).

## How it Works

1.  **Configuration**: Instantiate `DocstringIndexer` with a `Repository` object and a `Summarizer` (configured with your desired LLM, e.g., OpenAI, Anthropic, Google). An embedding function (`embed_fn`) can also be provided if you wish to use a custom embedding model; otherwise, `DocstringIndexer` will use a default embedding function (based on `sentence-transformers`, which is included in the standard installation).

 

```python
from kit import Repository, DocstringIndexer, Summarizer
from kit.llms.openai import OpenAIConfig # For configuring the summarization LLM

# 1. Initialize your Repository
repo = Repository("/path/to/your/codebase")

# 2. Configure and initialize the Summarizer
# It's good practice to specify the model you want for summarization.
# Summarizer defaults to OpenAIConfig() if no config is passed, which then
# might use environment variables (OPENAI_MODEL) or a default model from OpenAIConfig.
llm_summarizer_config = OpenAIConfig(model="gpt-4o") # Or "gpt-4-turbo", etc.
summarizer = Summarizer(repo, config=llm_summarizer_config)

# 3. Initialize DocstringIndexer
# By default, DocstringIndexer now uses SentenceTransformer('all-MiniLM-L6-v2')
# for embeddings, so you don't need to provide an embed_fn for basic usage.
indexer = DocstringIndexer(repo, summarizer)

# 4. Build the index
# This will process the repository, generate summaries, and create embeddings.
indexer.build()

# After building, you can query the index using a SummarySearcher.

# Option 1: Manually create a SummarySearcher (traditional way)
# from kit import SummarySearcher
# searcher_manual = SummarySearcher(indexer)

# Option 2: Use the convenient get_searcher() method (recommended)
searcher = indexer.get_searcher()

# Now you can use the searcher
results = searcher.search("your query here", top_k=3)
for result in results:
    print(f"Found: {result.get('metadata', {}).get('file_path')}::{result.get('metadata', {}).get('symbol_name')}")
    print(f"Summary: {result.get('metadata', {}).get('summary')}")
    print(f"Score: {result.get('score')}")
    print("---")
```

### Using a Custom Embedding Function (Optional)

If you want to use a different embedding model or a custom embedding function, you can pass it to the `DocstringIndexer` during initialization. The function should take a string as input and return a list of floats (the embedding vector).

For example, if you wanted to use a different model from the `sentence-transformers` library:

```python
from kit import Repository, DocstringIndexer, Summarizer
from kit.llms.openai import OpenAIConfig
from sentence_transformers import SentenceTransformer # Make sure you have this installed

repo = Repository("/path/to/your/codebase")
llm_summarizer_config = OpenAIConfig(model="gpt-4o")
summarizer = Summarizer(repo, config=llm_summarizer_config)

# Load a specific sentence-transformer model
# You can find available models at https://www.sbert.net/docs/pretrained_models.html
custom_st_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def custom_embedding_function(text_to_embed: str):
    embedding_vector = custom_st_model.encode(text_to_embed)
    return embedding_vector.tolist()

# Initialize DocstringIndexer with your custom embedding function
indexer_custom = DocstringIndexer(repo, summarizer, embed_fn=custom_embedding_function)

indexer_custom.build()
```

This approach gives you flexibility if the default embedding model doesn't meet your specific needs.

## Inspecting the Indexed Data (Optional)

After building the index, you might want to inspect its raw contents to understand what was stored. This can be useful for debugging or exploration. The exact method depends on the `VectorDBBackend` being used.

If you're using the default `ChromaDBBackend` (or have explicitly configured it), you can access the underlying ChromaDB collection and retrieve entries.

```python
# Assuming 'indexer' is your DocstringIndexer instance after 'indexer.build()' has run.
# And 'indexer.backend' is an instance of ChromaDBBackend.

if hasattr(indexer.backend, 'collection'):
    chroma_collection = indexer.backend.collection
    print(f"Inspecting ChromaDB collection: {chroma_collection.name}")
    print(f"Number of items: {chroma_collection.count()}")

    # Retrieve the first few items (e.g., 3)
    # We include 'metadatas' and 'documents' (which holds the summary text).
    # 'embeddings' are excluded for brevity.
    retrieved_data = chroma_collection.get(
        limit=3,
        include=['metadatas', 'documents'] 
    )

    if retrieved_data and retrieved_data.get('ids'):
        for i in range(len(retrieved_data['ids'])):
            item_id = retrieved_data['ids'][i]
            # The 'document' is the summary text that was embedded.
            summary_text = retrieved_data['documents'][i] if retrieved_data['documents'] else "N/A"
            # 'metadata' contains file_path, symbol_name, original summary, etc.
            metadata = retrieved_data['metadatas'][i] if retrieved_data['metadatas'] else {}
            
            print(f"\n--- Item {i+1} ---")
            print(f"  ID (in Chroma): {item_id}")
            print(f"  Stored Summary (Document): {summary_text}")
            print(f"  Metadata:")
            for key, value in metadata.items():
                print(f"    {key}: {value}")
    else:
        print("No items found in the collection or collection is empty.")
else:
    print("The configured backend does not seem to be ChromaDB or doesn't expose a 'collection' attribute for direct inspection this way.")

```

**Expected Output from Inspection:**

Running the inspection code above might produce output like this:

```text
Inspecting ChromaDB collection: kit_docstring_index
Number of items: 10 # Or however many items are in your test repo index

--- Item 1 ---
  ID (in Chroma): utils.py::greet
  Stored Summary (Document): The `greet` function in the `utils.py` file is designed to generate a friendly greeting message...
  Metadata:
    file_path: utils.py
    level: symbol
    summary: The `greet` function in the `utils.py` file is designed to generate a friendly greeting message...
    symbol_name: greet
    symbol_type: function

--- Item 2 ---
  ID (in Chroma): app.py::main
  Stored Summary (Document): The `main` function in `app.py` demonstrates a simple authentication workflow...
  Metadata:
    file_path: app.py
    level: symbol
    summary: The `main` function in `app.py` demonstrates a simple authentication workflow...
    symbol_name: main
    symbol_type: function

... (and so on)
```

This shows that each entry in the ChromaDB collection has:
- An `id` (often `file_path::symbol_name`).
- The `document` field, which is the text of the summary that was embedded.
- `metadata` containing details like `file_path`, `symbol_name`, `symbol_type`, `level`, and often a redundant copy of the `summary` itself.

Knowing the structure of this stored data can be very helpful when working with search results or debugging the indexing process.

### Symbol-Level Indexing

<Aside type="caution" title="Alpha Feature: Symbol-Level Indexing">
  Symbol-level indexing is an advanced alpha feature. While powerful, it may require more resources and is undergoing active development. Feedback is highly appreciated.
</Aside>

For more granular search, you can instruct `DocstringIndexer` to create summaries for individual **functions and classes** within your files. This allows for highly specific semantic queries like "find the class that manages database connections" or "what function handles user authentication?"

To enable symbol-level indexing, pass `level="symbol"` to `build()`:

```python
# Build a symbol-level index
indexer.build(level="symbol", file_extensions=[".py"], force=True)
```

When `level="symbol"`:
*   `DocstringIndexer` iterates through files, then extracts symbols (functions, classes) from each file using `repo.extract_symbols()`.
*   It then calls `summarizer.summarize_function()` or `summarizer.summarize_class()` for each symbol.
*   The resulting embeddings are stored with metadata including:
    *   `file_path`: The path to the file containing the symbol.
    *   `symbol_name`: The name of the function or class (e.g., `my_function`, `MyClass`, `MyClass.my_method`).
    *   `symbol_type`: The type of symbol (e.g., "FUNCTION", "CLASS", "METHOD").
    *   `summary`: The LLM-generated summary of the symbol.
    *   `level`: Set to `"symbol"`.

3.  **Querying**: Use `SummarySearcher` to find relevant summaries.

    ```python
    from kit import SummarySearcher

    searcher = SummarySearcher(indexer) # Pass the built indexer
    results = searcher.search("user authentication logic", top_k=3)

    for res in results:
        print(f"Score: {res['score']:.4f}")
        if res.get('level') == 'symbol':
            print(f"  Symbol: {res['symbol_name']} ({res['symbol_type']}) in {res['file_path']}")
        else:
            print(f"  File: {res['file_path']}")
        print(f"  Summary: {res['summary'][:100]}...")
        print("---")
    ```
    The `results` will contain the summary and associated metadata, including the `level` and symbol details if applicable.

## Quick start

```python
import kit
from sentence_transformers import SentenceTransformer

repo = kit.Repository("/path/to/your/project")

# 1. LLM summarizer (make sure OPENAI_API_KEY / etc. is set)
summarizer = repo.get_summarizer()

# 2. Embedding function (any model that returns list[float])
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_fn = lambda txt: embed_model.encode(txt).tolist()

# 3. Build the index (stored in .kit/docstring_db)
indexer = kit.DocstringIndexer(repo, summarizer)
indexer.build()

# 4. Search
searcher = kit.SummarySearcher(indexer)
for hit in searcher.search("retry back-off", top_k=5):
    print(hit["file"], "→", hit["summary"])
```

### Storage details

`DocstringIndexer` delegates persistence to any
`kit.vector_searcher.VectorDBBackend`.  The default backend is
[`Chroma`](https://docs.trychroma.com/) and lives in
`.kit/docstring_db/` inside your repo.

## Use Cases

*   **Semantic Code Search**: Find code by describing what it *does*, not just
    what keywords it contains. (e.g., “retry back-off logic” instead of trying to
    guess variable names like `exponential_delay` or `MAX_RETRIES`).
*   **Onboarding**: Quickly understand what different parts of a codebase are for.
*   **Automated Documentation**: Use the summaries as a starting point for API docs.
*   **Codebase Q&A**: As shown in the [Codebase Q&A Bot tutorial](/docs/tutorials/codebase-qa-bot), combine `SummarySearcher` with an LLM to answer questions about your code, using summaries to find relevant context at either the file or symbol level.


## API reference

Check docs for [`DocstringIndexer`](/docs/api/docstring-indexer) and [`SummarySearcher`](/docs/api/summary-searcher) for full signatures.
```

File: /Users/darin/docs/kit/core-concepts/llm-context-best-practices.mdx
```mdx
---
title: LLM Best Practices
---

import { Aside } from '@astrojs/starlight/components';

Providing the right context to a Large Language Model (LLM) is critical for getting accurate and relevant results when building AI developer tools with `kit`. This guide outlines best practices for assembling context using `kit` features.

### 1. File Tree (`repo.get_file_tree`)

*   **Context:** Provides the overall structure of the repository or specific directories.
*   **Use Cases:** Understanding project layout, locating relevant modules.
*   **Prompting Tip:** Include the file tree when asking the LLM about high-level architecture or where to find specific functionality.

```yaml
# Example Context Block
Repository File Tree (partial):
src/
  __init__.py
  core/
    repo.py
    search.py
  utils/
    parsing.py
tests/
  test_repo.py
README.md
```

<Aside type="caution">
  Use depth limits or filtering for large projects to avoid overwhelming the LLM.
</Aside>

### 2. Symbols (`repo.get_symbols`)

*   **Context:** Lists functions, classes, variables, etc., within specified files.
*   **Use Cases:** Understanding the code within a file, finding specific definitions, providing context for code generation/modification tasks.
*   **Prompting Tip:** Clearly label the file path associated with the symbols.

```yaml
# Example Context Block
Symbols in src/core/repo.py:
- class Repo:
  - def __init__(self, path):
  - def get_symbols(self, file_paths):
  - def search_semantic(self, query):
- function _validate_path(path):
```

<Aside type="note">
  Filter symbols to relevant files/modules when possible.
</Aside>

### 3. Code Snippets (via Symbols or `get_file_content`)

*   **Context:** The actual source code of specific functions, classes, or entire files.
*   **Use Cases:** Detailed code review, bug finding, explanation, modification.
*   **Prompting Tip:** Provide the code for symbols identified as relevant by other context methods (e.g., symbols mentioned in a diff, search results).

```python
# Example Context Block
Code for Repo.search_semantic in src/core/repo.py:

def search_semantic(self, query):
    # ... implementation ...
    pass
```

<Aside type="note">
  Clearly identify chunks in the prompt and prefer symbol-based chunking over line-based chunking when appropriate.
</Aside>

### 4. Text Search Results (`repo.search_text`)

*   **Context:** Lines of code matching a specific text query.
*   **Use Cases:** Finding specific variable names, API calls, error messages.
*   **Prompting Tip:** Include the search query and clearly label the results.

```yaml
# Example Context Block
Text search results for "database connection":
- src/db/connect.py:15: conn = connect_database()
- src/config.py:8: DATABASE_URL = "..."
```

<Aside type="note">
  Clearly specify the search query used to generate the results.
</Aside>

### 5. Symbol Usages (`repo.find_symbol_usages`)

*   **Context:** Where a specific symbol (function, class) is used or called throughout the codebase. This method finds definitions and textual occurrences.
*   **Use Cases:** Understanding the impact of changing a function, finding examples of how an API is used, basic dependency analysis.
*   **Prompting Tip:** Specify the symbol whose usages are being listed.

```yaml
# Example Context Block
Usages of function connect_database (defined in src/db/connect.py):
- src/app.py:50: db_conn = connect_database()
- tests/test_db.py:12: mock_connect = mock(connect_database)
```

<Aside type="note">
  Clearly indicate the symbol whose usages are being shown.
</Aside>

### 6. Semantic Search Results (`repo.search_semantic`)

*   **Context:** Code chunks semantically similar to a natural language query.
*   **Use Cases:** Finding code related to a concept (e.g., "user authentication logic"), exploring related functionality.
*   **Prompting Tip:** Include the semantic query and label the results clearly.

```
# Example Context Block
Semantic search results for "user login handling":
- Chunk from src/auth/login.py (lines 25-40):
    def handle_login(username, password):
        # ... validation logic ...
  
- Chunk from src/models/user.py (lines 10-15):
    class User:
        # ... attributes ...
```

<Aside type="note">
  Indicate that the results are from a semantic search, as the matches might not be exact text matches.
</Aside>

### 7. Diff Content

*   **Context:** The specific lines added, removed, or modified in a changeset (e.g., a Git diff).
*   **Use Cases:** Code review, understanding specific changes in a PR or commit.
*   **Prompting Tip:** Clearly mark the diff section in the context.

```diff
# Example Context Block
Code Diff:
--- a/src/utils/parsing.py
+++ b/src/utils/parsing.py
@@ -10,5 +10,6 @@
 def parse_data(raw_data):
     # Extended parsing logic
+    data = preprocess(raw_data)
     return json.loads(data)

```

<Aside type="note">
  Pair this context with specific line numbers for targeted analysis.
</Aside>

### 8. Vector Search Results (`repo.search_vectors`)

*   **Context:** Code chunks similar to a given vector representation.
*   **Use Cases:** Finding code related to a concept (e.g., "user authentication logic"), exploring related functionality.
*   **Prompting Tip:** Include the vector query and label the results clearly.

```
# Example Context Block
Vector search results for "user login handling":
- Chunk from src/auth/login.py (lines 25-40):
    def handle_login(username, password):
        # ... validation logic ...

- Chunk from src/models/user.py (lines 10-15):
    class User:
        # ... attributes ...
```

<Aside type="note">
  Indicate that the results are from a vector search, as the matches might not be exact text matches.
</Aside>

```

File: /Users/darin/docs/kit/api/summary-searcher.mdx
```mdx
---
title: SummarySearcher API
description: API documentation for the SummarySearcher class.
---

The `SummarySearcher` class provides a simple way to query an index built by [`DocstringIndexer`](/api/docstring-indexer). It takes a search query, embeds it using the same embedding function used for indexing, and retrieves the most semantically similar summaries from the vector database.

## Constructor

**Class: `SummarySearcher`**
*(defined in `kit/docstring_indexer.py`)*

The `SummarySearcher` is typically initialized with an instance of `DocstringIndexer`. It uses the `DocstringIndexer`'s configured backend and embedding function to perform searches.

```python
from kit.docstring_indexer import DocstringIndexer, SummarySearcher

# Assuming 'indexer' is an already initialized DocstringIndexer instance
# indexer = DocstringIndexer(repo=my_repo, summarizer=my_summarizer)
# indexer.build() # Ensure the index is built

searcher = SummarySearcher(indexer=indexer)
```

**Parameters:**

*   **`indexer`** (`DocstringIndexer`, required):
    An instance of `DocstringIndexer` that has been configured and preferably has had its `build()` method called. The `SummarySearcher` will use this indexer's `backend` and `embed_fn`. See the [`DocstringIndexer API docs`](./docstring-indexer) for more details on the indexer.

## Methods

### `search`

**Method: `SummarySearcher.search`**
*(defined in `kit/docstring_indexer.py`)*

Embeds the given `query` string and searches the vector database (via the indexer's backend) for the `top_k` most similar document summaries.

```python
query_text = "How is user authentication handled?"
results = searcher.search(query=query_text, top_k=3)

for result in results:
    print(f"Found in: {result.get('file_path')} ({result.get('symbol_name')})")
    print(f"Score: {result.get('score')}")
    print(f"Summary: {result.get('summary')}")
    print("----")} 
```

**Parameters:**

*   **`query`** (`str`, required):
    The natural language query string to search for.
*   **`top_k`** (`int`, default: `5`):
    The maximum number of search results to return.

**Returns:** `List[Dict[str, Any]]`

    A list of dictionaries, where each dictionary represents a search hit.
    Each hit typically includes metadata, a score, an ID, and the summary text.

```

File: /Users/darin/docs/kit/core-concepts/repository-api.mdx
```mdx
---
title: The Repository Interface
---

import { Aside } from "@astrojs/starlight/components";

The `kit.Repository` object is the backbone of the library. It serves as your primary interface for accessing, analyzing, and understanding codebases, regardless of their language or location (local path or remote Git URL).

## Why the `Repository` Object?

Interacting directly with code across different languages, file structures, and potential locations (local vs. remote) can be cumbersome. The `Repository` object provides a **unified and consistent abstraction layer** to handle this complexity.

Key benefits include:

- **Unified Access:** Provides a single entry point to read files, extract code structures (symbols), perform searches, and more.
- **Location Agnostic:** Works seamlessly with both local file paths and remote Git repository URLs (handling cloning and caching automatically when needed).
- **Language Abstraction:** Leverages `tree-sitter` parsers under the hood to understand the syntax of various programming languages, allowing you to work with symbols (functions, classes, etc.) in a standardized way.
- **Foundation for Tools:** Acts as the foundation upon which you can build higher-level developer tools and workflows, such as documentation generators, AI code reviewers, or semantic search engines.

## What Can You Do with a `Repository`?

Once you instantiate a `Repository` object pointing to your target codebase:

```python
from kit import Repository

# Point to a local project
my_repo = Repository("/path/to/local/project")

# Or point to a remote GitHub repo
# github_repo = Repository("https://github.com/owner/repo-name")
```

You can perform various code intelligence tasks:

- **Explore Structure:** Get the file tree (`.get_file_tree()`).
- **Read Content:** Access the raw content of specific files (`.get_file_content()`).
- **Understand Code:** Extract detailed information about functions, classes, and other symbols (`.extract_symbols()`).
- **Analyze Dependencies:** Find where symbols are defined and used (`.find_symbol_usages()`).
- **Search:** Perform literal text searches (`.search_text()`) or powerful semantic searches (`.search_semantic()`).
- **Prepare for LLMs:** Chunk code intelligently by lines or symbols (`.chunk_file_by_lines()`, `.chunk_file_by_symbols()`) and get code context around specific lines (`.extract_context_around_line()`).
- **Integrate with AI:** Obtain configured summarizers (`.get_summarizer()`) or vector searchers (`.get_vector_searcher()`) for advanced AI workflows.
- **Export Data:** Save the file tree, symbol information, or full repository index to structured formats like JSON (`.write_index()`, `.write_symbols()`, etc.).

The following table lists some of the key classes and tools you can access through the `Repository` object:

| Class/Tool         | Description                                    |
| ------------------ | ---------------------------------------------- |
| `Summarizer`       | Generate summaries of code using LLMs          |
| `VectorSearcher`   | Query vector index of code for semantic search |
| `DocstringIndexer` | Build vector index of LLM-generated summaries  |
| `SummarySearcher`  | Query that index                               |


<Aside type="tip">
  For a complete list of methods, parameters, and detailed usage examples,
  please refer to the **[Repository Class API Reference](/api/repository/)**.
</Aside>


<Aside type="note">
## File and Directory Exclusion (.gitignore support)

By default, kit automatically ignores files and directories listed in your `.gitignore` as well as `.git/` and its contents. This ensures your indexes, symbol extraction, and searches do not include build artifacts, dependencies, or version control internals.

**Override:**
- This behavior is the default. If you want to include ignored files, you can override this by modifying the `RepoMapper` logic (see `src/kit/repo_mapper.py`) or subclassing it with custom exclusion rules.
</Aside>

```

File: /Users/darin/docs/kit/api/docstring-indexer.mdx
```mdx
---
title: DocstringIndexer API
description: API documentation for the DocstringIndexer class.
---

The `DocstringIndexer` class is responsible for building a vector index of AI-generated code summaries (docstrings). It processes files in a repository, generates summaries for code symbols (or entire files), embeds these summaries, and stores them in a configurable vector database backend. Once an index is built, it can be queried using the [`SummarySearcher`](/api/summary-searcher) class.

## Constructor

**Class: `DocstringIndexer`**
*(defined in `kit/docstring_indexer.py`)*

```python
from kit import Repository, Summarizer
from kit.docstring_indexer import DocstringIndexer, EmbedFn # EmbedFn is Optional[Callable[[str], List[float]]]
from kit.vector_searcher import VectorDBBackend # Optional

# Example basic initialization
repo = Repository("/path/to/your/repo")
summarizer = Summarizer() # Assumes OPENAI_API_KEY is set or local model configured
indexer = DocstringIndexer(repo=repo, summarizer=summarizer)

# Example with custom embedding function and backend
# def my_custom_embed_fn(text: str) -> List[float]:
#     # ... your embedding logic ...
#     return [0.1, 0.2, ...]
#
# from kit.vector_searcher import ChromaDBBackend
# custom_backend = ChromaDBBackend(collection_name="my_custom_index", persist_dir="./my_chroma_db")
#
# indexer_custom = DocstringIndexer(
#     repo=repo,
#     summarizer=summarizer,
#     embed_fn=my_custom_embed_fn,
#     backend=custom_backend,
#     persist_dir="./my_custom_index_explicit_persist" # Can also be set directly on backend
# )
```

**Parameters:**

*   **`repo`** (`Repository`, required):
    An instance of `kit.Repository` pointing to the codebase to be indexed.
*   **`summarizer`** (`Summarizer`, required):
    An instance of `kit.Summarizer` used to generate summaries for code symbols or files.
*   **`embed_fn`** (`Optional[Callable[[str], List[float]]]`, default: `SentenceTransformer('all-MiniLM-L6-v2')`):
    A function that takes a string and returns its embedding (a list of floats).
    If `None`, a default embedding function using `sentence-transformers` (`all-MiniLM-L6-v2` model) will be used.
    The `sentence-transformers` package must be installed for the default to work (`pip install sentence-transformers`).
*   **`backend`** (`Optional[VectorDBBackend]`, default: `ChromaDBBackend`):
    The vector database backend to use for storing and querying embeddings.
    If `None`, a `ChromaDBBackend` instance will be created.
    The default collection name is `kit_docstring_index`.
*   **`persist_dir`** (`Optional[str]`, default: `'./.kit_index/' + repo_name_slug + '/docstrings'`):
    The directory where the vector database (e.g., ChromaDB) should persist its data.
    If `None`, a default path is constructed based on the repository name within a `.kit_index` directory in the current working directory.
    If a custom `backend` is provided, this parameter might be ignored if the backend itself has persistence configured. It's primarily used for the default `ChromaDBBackend` if no explicit `backend` is given or if the default backend needs a specific persistence path.

## Methods

### `build`

**Method: `DocstringIndexer.build`**
*(defined in `kit/docstring_indexer.py`)*

Builds or rebuilds the docstring index. It iterates through files in the repository (respecting `.gitignore` and `file_extensions`), extracts symbols or uses whole file content based on the `level`, generates summaries, embeds them, and adds them to the vector database. It also handles caching to avoid re-processing unchanged symbols/files.

```python
# Build the index (symbol-level by default for .py files)
indexer.build()

# Force a rebuild, ignoring any existing cache
indexer.build(force=True)

# Index at file level instead of symbol level
indexer.build(level="file")

# Index only specific file extensions
indexer.build(file_extensions=[".py", ".mdx"])
```

**Parameters:**

*   **`force`** (`bool`, default: `False`):
    If `True`, the entire index is rebuilt, ignoring any existing cache and potentially overwriting existing data in the backend.
    If `False`, uses cached summaries/embeddings for unchanged code and only processes new/modified code. It also avoids re-initializing the backend if it already contains data, unless changes are detected.
*   **`level`** (`str`, default: `'symbol'`):
    The granularity of indexing.
    - `'symbol'`: Extracts and summarizes individual symbols (functions, classes, methods) from files.
    - `'file'`: Summarizes the entire content of each file.
*   **`file_extensions`** (`Optional[List[str]]`, default: `None` (uses Repository's default, typically .py)):
    A list of file extensions (e.g., `['.py', '.md']`) to include in the indexing process.
    If `None`, uses the default behavior of the `Repository` instance, which typically focuses on Python files but can be configured.

**Returns:** `None`

### `get_searcher`

**Method: `DocstringIndexer.get_searcher`**
*(defined in `kit/docstring_indexer.py`)*

Returns a `SummarySearcher` instance that is configured to query the index managed by this `DocstringIndexer`.

This provides a convenient way to obtain a search interface after the indexer has been built or loaded, without needing to manually instantiate `SummarySearcher`.

```python
# Assuming 'indexer' is an initialized DocstringIndexer instance
# indexer.build() # or it has been loaded with a pre-built index

search_interface = indexer.get_searcher()
results = search_interface.search("my search query", top_k=3)

for result in results:
    print(result)
```

**Parameters:** None

**Returns:** `SummarySearcher`

    An instance of `SummarySearcher` linked to this indexer.


```

File: /Users/darin/docs/kit/core-concepts/dependency-analysis.mdx
```mdx
---
title: Dependency Analysis
---

import { Aside } from '@astrojs/starlight/components';

The dependency analysis feature in `kit` allows you to map, visualize, and analyze the relationships between different components in your codebase. This helps you understand complex codebases, identify potential refactoring opportunities, detect circular dependencies, and prepare dependency context for large language models.

## Why Dependency Analysis?

Understanding dependencies in a codebase is crucial for:

- **Codebase Understanding:** Quickly grasp how different modules interact with each other.
- **Refactoring Planning:** Identify modules with excessive dependencies or cyclic relationships that might benefit from refactoring.
- **Technical Debt Assessment:** Map dependencies to visualize potential areas of technical debt or architectural concerns.
- **Impact Analysis:** Determine the potential impact of changes to specific components.
- **LLM Context Preparation:** Generate concise, structured descriptions of codebase architecture for LLM context.

## Getting Started

You can access the dependency analyzer through the `Repository` object:

```python
from kit import Repository

# Load your codebase
repo = Repository("/path/to/your/codebase")

# Get a language-specific dependency analyzer
# Currently supports 'python' and 'terraform'
analyzer = repo.get_dependency_analyzer('python')  # or 'terraform'

# Build the dependency graph
graph = analyzer.build_dependency_graph()

print(f"Found {len(graph)} components in the dependency graph")
```

## Exploring Dependencies

Once you've built the dependency graph, you can explore it in various ways:

```python
# Find cycles (circular dependencies)
cycles = analyzer.find_cycles()
if cycles:
    print(f"Found {len(cycles)} circular dependencies:")
    for cycle in cycles[:5]:
        print(f"  {' → '.join(cycle)} → {cycle[0]}")

# Get dependencies for a specific module
module_deps = analyzer.get_resource_dependencies('module_name')
print(f"Module depends on: {module_deps}")

# Get dependents (modules that depend on a specific module)
dependents = analyzer.get_dependents('module_name')
print(f"Modules that depend on this: {dependents}")
```

## Visualizing Dependencies

You can visualize the dependency graph using common formats like DOT, GraphML, or JSON:

```python
# Export to DOT format (for use with tools like Graphviz)
analyzer.export_dependency_graph(
    output_format="dot",
    output_path="dependency_graph.dot"
)

# Generate a PNG visualization
analyzer.visualize_dependencies(
    output_path="dependency_visualization.png",
    format="png"  # supports 'png', 'svg', or 'pdf'
)
```

<Aside type="note">
  Visualization requires the Graphviz software to be installed on your system.
</Aside>

## LLM Context Generation

One of the most powerful features of the dependency analyzer is its ability to generate concise, LLM-friendly context about your codebase structure:

```python
# Generate markdown context for LLMs
context = analyzer.generate_llm_context(
    output_format="markdown",
    output_path="dependency_context.md",
    max_tokens=4000  # approximate token limit
)
```

The generated context includes:
- Overall statistics (component count, type breakdown)
- Key components with high connectivity
- Circular dependency information
- Language-specific insights (e.g., import patterns for Python, resource relationships for Terraform)

## Language-Specific Features

### Python Dependency Analysis

The Python dependency analyzer maps import relationships between modules:

```python
# Get a Python-specific analyzer
python_analyzer = repo.get_dependency_analyzer('python')

# Build the graph
python_analyzer.build_dependency_graph()

# Find standard library vs. third-party dependencies
report = python_analyzer.generate_dependency_report()
print(f"Standard library imports: {len(report['standard_library_imports'])}")
print(f"Third-party imports: {len(report['third_party_imports'])}")
```

### Terraform Dependency Analysis

The Terraform dependency analyzer maps relationships between infrastructure resources:

```python
# Get a Terraform-specific analyzer
terraform_analyzer = repo.get_dependency_analyzer('terraform')

# Build the graph
terraform_analyzer.build_dependency_graph()

# Find all resources of a specific type
s3_buckets = terraform_analyzer.get_resource_by_type("aws_s3_bucket")
```

Each resource in the graph includes its absolute file path, making it easy to locate resources in complex infrastructure codebases:

```
aws_launch_template.app (aws_launch_template) [File: /path/to/your/project/compute.tf]
```

<Aside type="tip">
  For complete API details, including all available methods and options, see the **[DependencyAnalyzer API Reference](/api/dependency-analyzer/)**.
</Aside>

## Advanced Usage

### Custom Dependency Analysis

If you have specific needs for your dependency analysis, you can extend the base `DependencyAnalyzer` class to create analyzers for other languages or frameworks:

```python
from kit.dependency_analyzer import DependencyAnalyzer

class CustomDependencyAnalyzer(DependencyAnalyzer):
    # Implement required abstract methods
    def build_dependency_graph(self):
        # Your custom logic here
        pass
        
    def export_dependency_graph(self, output_format="json", output_path=None):
        # Your custom export logic here
        pass
        
    def find_cycles(self):
        # Your custom cycle detection logic here
        pass
        
    def visualize_dependencies(self, output_path, format="png"):
        # Your custom visualization logic here
        pass
```

```

File: /Users/darin/docs/kit/api/repository.mdx
```mdx
---
title: Repository API
---

import { Aside } from '@astrojs/starlight/components';

This page details the methods and properties of the central `kit.Repository` class.

## Initialization

```python
from kit import Repository

# Initialize with a local path
local_repo = Repository("/path/to/your/local/project")

# Initialize with a remote URL (requires git)
# remote_repo = Repository("https://github.com/user/repo.git") 
```

## Core Methods

*   `index()`: Analyzes the repository.
*   `get_file_tree()`: Returns the file tree structure.
*   `get_file_content(file_path)`: Reads and returns the content of a specified file.
*   `extract_symbols(path)`: Extracts code symbols.
*   `search_semantic(query)`: Performs semantic search.
*   `get_summarizer()`: Gets the code summarizer.

## Creating a `Repository` Instance

To start using `kit`, first create an instance of the `Repository` class. This points `kit` to the codebase you want to analyze.

```python
from kit import Repository

# For a local directory
repository_instance = Repository(path_or_url="/path/to/local/project")

# For a remote Git repository (public or private)
# repository_instance = Repository(
#     path_or_url="https://github.com/owner/repo-name", 
#     github_token="YOUR_GITHUB_TOKEN",  # Optional: For private repos
#     cache_dir="/path/to/cache"       # Optional: For caching clones
# )
```

**Parameters:**

*   `path_or_url` (str): The path to a local directory or the URL of a remote Git repository.
*   `github_token` (Optional[str]): A GitHub personal access token required for cloning private repositories. Defaults to `None`.
*   `cache_dir` (Optional[str]): Path to a directory for caching cloned repositories. Defaults to a system temporary directory.

Once you have a `repository` object, you can call the following methods on it:

## `repository.get_file_tree()`

Returns the file tree structure of the repository.

```python
repository.get_file_tree() -> List[Dict[str, Any]]
```

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries, where each dictionary represents a file or directory with keys like `path`, `name`, `is_dir`, `size`.

## `repository.get_file_content()`

Reads and returns the content of a specified file within the repository as a string.

```python
repository.get_file_content(file_path: str) -> str
```

**Parameters:**

*   `file_path` (str): The path to the file, relative to the repository root.

**Returns:**

*   `str`: The content of the file.

**Raises:**

*   `FileNotFoundError`: If the file does not exist at the specified path.
*   `IOError`: If any other I/O error occurs during file reading.

## `repository.extract_symbols()`

Extracts code symbols (functions, classes, variables, etc.) from the repository.

```python
repository.extract_symbols(file_path: Optional[str] = None) -> List[Dict[str, Any]]
```

**Parameters:**

*   `file_path` (Optional[str]): If provided, extracts symbols only from this specific file path relative to the repo root. If `None`, extracts symbols from all supported files in the repository. Defaults to `None`.

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries, each representing a symbol with keys like `name`, `type`, `file`, `line_start`, `line_end`, `code`.

## `repository.search_text()`

Searches for literal text or regex patterns within files.

```python
repository.search_text(query: str, file_pattern: str = "*.py") -> List[Dict[str, Any]]
```

**Parameters:**

*   `query` (str): The text or regex pattern to search for.
*   `file_pattern` (str): A glob pattern to filter files to search within. Defaults to `"*.py"`.

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries representing search matches, with keys like `file`, `line_number`, `line_content`.

## `repository.chunk_file_by_lines()`

Chunks a file's content based on line count.

```python
repository.chunk_file_by_lines(file_path: str, max_lines: int = 50) -> List[str]
```

**Parameters:**

*   `file_path` (str): The path to the file (relative to repo root) to chunk.
*   `max_lines` (int): The maximum number of lines per chunk. Defaults to `50`.

**Returns:**

*   `List[str]`: A list of strings, where each string is a chunk of the file content.

## `repository.chunk_file_by_symbols()`

Chunks a file's content based on its top-level symbols (functions, classes).

```python
repository.chunk_file_by_symbols(file_path: str) -> List[Dict[str, Any]]
```

**Parameters:**

*   `file_path` (str): The path to the file (relative to repo root) to chunk.

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries, each representing a symbol chunk with keys like `name`, `type`, `code`.

## `repository.extract_context_around_line()`

Extracts the surrounding code context (typically the containing function or class) for a specific line number.

```python
repository.extract_context_around_line(file_path: str, line: int) -> Optional[Dict[str, Any]]
```

**Parameters:**

*   `file_path` (str): The path to the file (relative to repo root).
*   `line` (int): The (0-based) line number to find context for.

**Returns:**

*   `Optional[Dict[str, Any]]`: A dictionary representing the symbol context (with keys like `name`, `type`, `code`), or `None` if no context is found.

## `repository.index()`

Builds and returns a comprehensive index of the repository, including both the file tree and all extracted symbols.

```python
repository.index() -> Dict[str, Any]
```

**Returns:**

*   `Dict[str, Any]`: A dictionary containing the full index, typically with keys like `file_tree` and `symbols`.

## `repository.get_vector_searcher()`

Initializes and returns the `VectorSearcher` instance for performing semantic search.

```python
repository.get_vector_searcher(embed_fn=None, backend=None, persist_dir=None) -> VectorSearcher
```

**Parameters:**

*   `embed_fn` (Callable): **Required on first call.** A function that takes a list of strings and returns a list of embedding vectors.
*   `backend` (Optional[Any]): Specifies the vector database backend. If `None`, `kit` defaults to using `ChromaDBBackend`.
*   `persist_dir` (Optional[str]): Path to a directory to persist the vector index. If `None`, the `VectorSearcher` will default to `YOUR_REPO_PATH/.kit/vector_db/` for ChromaDB. Setting to `None` implies using this default persistence path for ChromaDB.

**Returns:**

*   `VectorSearcher`: An instance of the vector searcher configured for this repository.

(See [Configuring Semantic Search](/core-concepts/configuring-semantic-search) for more details.)

## `repository.search_semantic()`

Performs a semantic search query over the indexed codebase.

```python
repository.search_semantic(query: str, top_k: int = 5, embed_fn=None) -> List[Dict[str, Any]]
```

**Parameters:**

*   `query` (str): The natural language query to search for.
*   `top_k` (int): The maximum number of results to return. Defaults to `5`.
*   `embed_fn` (Callable): Required if the vector searcher hasn't been initialized yet.

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries representing the search results, typically including matched code snippets and relevance scores.

## `repository.find_symbol_usages()`

Finds definitions and references of a specific symbol across the repository.

```python
repository.find_symbol_usages(symbol_name: str, symbol_type: Optional[str] = None) -> List[Dict[str, Any]]
```

**Parameters:**

*   `symbol_name` (str): The name of the symbol to find usages for.
*   `symbol_type` (Optional[str]): Optionally restrict the search to a specific symbol type (e.g., 'function', 'class'). Defaults to `None` (search all types).

**Returns:**

*   `List[Dict[str, Any]]`: A list of dictionaries representing symbol usages, including file, line number, and context/snippet.

## `repository.write_index()`

Writes the full repository index (file tree and symbols) to a JSON file.

```python
repository.write_index(file_path: str) -> None
```

**Parameters:**

*   `file_path` (str): The path to the output JSON file.

## `repository.write_symbols()`

Writes extracted symbols to a JSON file.

```python
repository.write_symbols(file_path: str, symbols: Optional[list] = None) -> None
```

**Parameters:**

*   `file_path` (str): The path to the output JSON file.
*   `symbols` (Optional[list]): An optional list of symbol dictionaries to write. If `None`, writes all symbols extracted from the repository. Defaults to `None`.

## `repository.write_file_tree()`

Writes the repository file tree to a JSON file.

```python
repository.write_file_tree(file_path: str) -> None
```

**Parameters:**

*   `file_path` (str): The path to the output JSON file.

## `repository.write_symbol_usages()`

Writes the found usages of a specific symbol to a JSON file.

```python
repository.write_symbol_usages(symbol_name: str, file_path: str, symbol_type: Optional[str] = None) -> None
```

**Parameters:**

*   `symbol_name` (str): The name of the symbol whose usages were found.
*   `file_path` (str): The path to the output JSON file.
*   `symbol_type` (Optional[str]): The symbol type filter used when finding usages. Defaults to `None`.

## `repository.get_context_assembler()`

Convenience helper that returns a fresh `ContextAssembler` bound to this repository.
Use it instead of importing the class directly:

```python
assembler = repository.get_context_assembler()
assembler.add_diff(my_diff)
context_blob = assembler.format_context()
```

**Returns:**

* `ContextAssembler`: Ready-to-use assembler instance.

## `repository.get_summarizer()`


```

File: /Users/darin/docs/kit/core-concepts/semantic-search.mdx
```mdx
---
title: Semantic Searching
---
import { Aside } from '@astrojs/starlight/components';

<Aside type="caution" title="Experimental">
  Vector / semantic search is an early feature.  APIs, CLI commands, and index formats may change in future releases without notice.
</Aside>

<br />

kit supports semantic code search using vector embeddings and ChromaDB.

### How it works

- Chunks your codebase (by symbols or lines)
- Embeds each chunk using your chosen model (OpenAI, HuggingFace, etc)
- Stores embeddings in a local ChromaDB vector database
- Lets you search for code using natural language or code-like queries

### Example Usage

```python
from kit import Repository
from sentence_transformers import SentenceTransformer

# Use any embedding model you like
model = SentenceTransformer("all-MiniLM-L6-v2")
def embed_fn(text):
    return model.encode([text])[0].tolist()

repo = Repository("/path/to/codebase")
vs = repo.get_vector_searcher(embed_fn=embed_fn)
vs.build_index()  # Index all code chunks (run once, or after code changes)

results = repo.search_semantic("How is authentication handled?", embed_fn=embed_fn)
for hit in results:
    print(hit["file"], hit.get("name"), hit.get("type"), hit.get("code"))
# Example output:
# src/kit/auth.py login function def login(...): ...
# src/kit/config.py AUTH_CONFIG variable AUTH_CONFIG = {...}
```

### Choosing an Embedding Model

`kit` is model-agnostic: pass any function `str -> List[float]`.

* **Local (open-source)** – e.g. [`sentence-transformers`](https://www.sbert.net/) models like `all-MiniLM-L6-v2` (see example above). 100 MB-ish download, fast CPU inference.
* **Cloud API** – e.g. OpenAI `text-embedding-3-small`. Define:
  ```python
  import openai
  def embed_fn(text: str):
      resp = openai.embeddings.create(model="text-embedding-3-small", input=[text])
      return resp.data[0].embedding
  ```
* **Batching** – `VectorSearcher` will attempt to call your `embed_fn` with a *list* of texts for efficiency.  If your function only supports single strings it still works (falls back internally).

### Chunking Strategy

`vs.build_index(chunk_by="symbols")` (default) extracts functions/classes/variables via the existing AST parser.  This is usually what you want.

* `chunk_by="lines"` splits code into ~50-line blocks – useful for languages where symbol extraction isn't supported yet.
* You can re-index at any time; the previous collection is cleared automatically.

### Persisting & Re-using an Index

The index lives under `.kit/vector_db` by default (one Chroma collection per path).

```python
vs = repo.get_vector_searcher(embed_fn, persist_dir=".kit/my_index")
vs.build_index()
# … later …
searcher = repo.get_vector_searcher(embed_fn, persist_dir=".kit/my_index")
results = searcher.search("add user authentication")
```

### Docstring index

Prefer *meaning-first* search?  Instead of embedding raw code you can build an
index of LLM-generated summaries:

```text
DocstringIndexer → SummarySearcher
```

See **[Docstring-Based Vector Index](/docs/core-concepts/docstring-indexing)**
for details.

### Feeding Results to an LLM

Combine `VectorSearcher` with `ContextAssembler` to build an LLM prompt containing only *relevant* code:

```python
from kit import ContextAssembler
chunks = repo.search_semantic("jwt auth flow", embed_fn=embed_fn, top_k=10)
assembler = ContextAssembler(max_chars=12_000)
context = assembler.from_chunks(chunks)
llm_response = my_llm.chat(prompt + context)
```

### Limitations & Tips

* Indexing a very large monorepo may take minutes: consider running on CI and committing `.kit/vector_db`.
* Embeddings are language-agnostic – comments & docs influence similarity too.  Clean code/comments improve search.
* Exact-keyword search (`repo.search_text()`) can still be faster for quick look-ups; combine both techniques.

<Aside type="note">
  The CLI (`kit search` / `kit serve`) currently performs **text** search only. A semantic variant is planned.
</Aside>

```

File: /Users/darin/docs/kit/development/running-tests.mdx
```mdx
---
title: Running Tests
---

To run tests using uv and pytest, first ensure you have the development dependencies installed:

```sh
# Install all deps
uv pip install -e .
```

Then, run the full test suite using:

```sh
uv run pytest
```

Or to run a specific test file:

```sh
uv run pytest tests/test_hcl_symbols.py
```

## Code Style and Formatting

Kit uses [Ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting with a line length of 120 characters. Our configuration can be found in `pyproject.toml`.

To check your code against our style guidelines:

```sh
# Run linting checks
ruff check .

# Check format (doesn't modify files)
ruff format --check .
```

To automatically fix linting issues and format your code:

```sh
# Fix linting issues
ruff check --fix .

# Format code
ruff format .
```

These checks are enforced in CI, so we recommend running them locally before pushing changes.

```

File: /Users/darin/docs/kit/core-concepts/tool-calling-with-kit.mdx
```mdx
---
title: Tool-Calling with kit
subtitle: Practical patterns for letting your LLM drive kit's code-intelligence APIs
---

Modern LLM runtimes (OpenAI *function-calling*, Anthropic *tools*, etc.) let you hand the model a **menu of functions** in JSON-Schema form. The model then plans its own calls – no hard-coded if/else trees required. 

With `kit` you can  expose its code-intelligence primitives (search, symbol extraction, summaries, etc) and let the LLM decide which one to execute in each turn.  Your app stays declarative: *"Here are the tools, here is the user's question, please help."*

In practice that means you can drop `kit` into an existing chat agent with by just registering the schema and making the calls as needed. The rest of this guide shows the small amount of glue code needed and the conversational patterns that emerge.

You may also be interested in kit's [MCP integration](../mcp/using-kit-with-mcp), which can achieve similar goals.

`kit` exposes its code-intelligence primitives as **callable tools**.  Inside Python you can grab the JSON-Schema list with a single helper (`kit.get_tool_schemas()`) and hand that straight to your LLM runtime.  Once the schema is registered the model can decide _when_ to call:

* `open_repository`
* `search_code`
* `extract_symbols`
* `find_symbol_usages`
* `get_file_tree`, `get_file_content`
* `get_code_summary`

This page shows the minimal JSON you need, the decision patterns the model will follow, and a multi-turn example.

## 1  Register the tools

### OpenAI Chat Completions

```python
from openai import OpenAI
from kit import get_tool_schemas

client = OpenAI()

# JSON-Schema for every kit tool
functions = get_tool_schemas()

messages = [
    {"role": "system", "content": "You are an AI software engineer, some refer to as the 'Scottie Scheffler of Programming'. Feel free to call tools when you need context."},
]
```

`functions` is a list of JSON-Schema objects. Pass it directly as the `tools`/`functions` parameter to `client.chat.completions.create()`.

### Anthropic (messages-v2)

```python
from anthropic import Anthropic
anthropic = Anthropic()

# JSON-Schema for every kit tool
functions = get_tool_schemas()

response = anthropic.messages.create(
    model="claude-3-7-sonnet-20250219",
    system="You are an AI software engineer…",
    tools=functions,
    messages=[{"role": "user", "content": "I got a test failure around FooBar.  Help me."}],
)
```

## 2  When should the model call which tool?

Below is the heuristic kit's own prompts (and our internal dataset) encourage.  You **don't** need to hard-code this logic—the LLM will pick it up from the tool names / descriptions—but understanding the flow helps you craft better conversation instructions.

| Situation | Suggested tool(s) |
|-----------|-------------------|
| No repo open yet | `open_repository` (first turn) |
| "What files mention X?" | `search_code` (fast regex) |
| "Show me the function/class definition" | `get_file_content` *or* `extract_symbols` |
| "Where else is `my_func` used?" | 1) `extract_symbols` (file-level) → 2) `find_symbol_usages` |
| "Summarize this file/function for the PR description" | `get_code_summary` |
| IDE-like navigation | `get_file_tree` + `get_file_content` |

A **typical multi-turn session**:

```
User: I keep getting KeyError("user_id") in prod.

Assistant (tool call): search_code {"repo_id": "42", "query": "KeyError(\"user_id\")"}

Tool result → 3 hits returned (files + line numbers)

Assistant: The error originates in `auth/session.py` line 88.  Shall I show you that code?

User: yes, show me.

Assistant (tool call): get_file_content {"repo_id": "42", "file_path": "auth/session.py"}

Tool result → file text

Assistant: Here is the snippet … (explanatory text)
```

## 3  Prompt orchestration: system / developer messages

Tool-calling conversations have **three channels of intent**:

1. **System prompt** – your immutable instructions (e.g. *"You are an AI software-engineer agent."*)  
2. **Developer prompt** – _app-level_ steering: *"If the user asks for code you have not seen, call `get_file_content` first."*  
3. **User prompt** – the human's actual message.

`kit` does *not* impose a format—you simply include the JSON-schema from `kit.get_tool_schemas()` in your `tools` / `functions` field and add whatever system/developer guidance you choose.
A common pattern is:

```python
system = """You are an AI software-engineer.
Feel free to call tools when they help you answer precisely.
When showing code, prefer the smallest snippet that answers the question.
"""

developer = """Available repos are already open in the session.
Call `search_code` before you attempt to answer questions like
  *"Where is X defined?"* or *"Show references to Y"*.
Use `get_code_summary` before writing long explanations of unfamiliar files.
"""

messages = [
    {"role": "system", "content": system},
    {"role": "system", "name": "dev-instructions", "content": developer},
    {"role": "user", "content": user_query},
]
```

Because the developer message is separate from the user's content it can be updated dynamically by your app (e.g. after each tool result) without contaminating the visible chat transcript.

## 4  Streaming multi-tool conversations

Nothing prevents the LLM from chaining calls:

1. `extract_symbols` on the failing file.
2. Pick the function, then `get_code_summary` for a concise explanation.

Frameworks like **LangChain**, **LlamaIndex** or **CrewAI** can route these calls automatically when you surface kit's tool schema as their "tool" object.

```python
from langchain_community.tools import Tool
kit_tools = [Tool.from_mcp_schema(t, call_kit_server) for t in functions]
```

## 5  Security considerations

`get_file_content` streams raw code.  If you expose kit to an external service:

* Restrict `open_repository` to a safe path.
* Consider stripping secrets from returned text.
* Disable `get_file_content` for un-trusted queries and rely on `extract_symbols` + `get_code_summary` instead.

## 6  In-process (no extra server)

If your application is **already written in Python** you don't have to spawn any servers at all—just keep a `Repository` instance in memory and expose thin wrappers as tools/functions:

```python
from typing import TypedDict
from kit import Repository

repo = Repository("/path/to/repo")

class SearchArgs(TypedDict):
    query: str
    pattern: str

def search_code(args: SearchArgs):
    return repo.search_text(args["query"], file_pattern=args.get("pattern", "*.py"))
```

Then register the wrapper with your tool-calling framework:

```python
from openai import OpenAI
client = OpenAI()

functions = [
    {
        "name": "search_code",
        "description": "Regex search across the active repository",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "pattern": {"type": "string", "default": "*.py"},
            },
            "required": ["query"],
        },
    },
]

client.chat.completions.create(
    model="gpt-4o",
    tools=functions,
    messages=[...]
)
```

Because everything stays in the same process you avoid IPC/JSON overhead and can share caches (e.g. the `RepoMapper` symbol index) across calls.

**Tip:** if you later need multi-language tooling or a separate sandbox you can still swap in the MCP server without touching your prompt logic—the function schema stays the same.

---
```

File: /Users/darin/docs/kit/development/roadmap.mdx
```mdx
---
title: Kit Project Roadmap
---

import { Card, CardGrid } from '@astrojs/starlight/components';

This document outlines the current capabilities of the `kit` library and a potential roadmap for its future development. It's a living document and will evolve as the project progresses.

## Core Philosophy

`kit` aims to be a comprehensive Python toolkit for advanced code understanding, analysis, and interaction, with a strong emphasis on leveraging Large Language Models (LLMs) where appropriate. It's designed to be modular, extensible, and developer-friendly.

## Current Capabilities

As of now, `kit` provides the following core functionalities:

<CardGrid>
	<Card title="Repository Interaction">
		The `Repository` class acts as a central hub for accessing various code analysis features for a given codebase.
	</Card>
	<Card title="Code Mapping & Symbols">
		`RepoMapper` provides structural and symbol information from code files, using Tree-sitter for multi-language support and incremental updates.
	</Card>
	<Card title="Code Summarization">
		The `Summarizer` class, supporting multiple LLM providers (e.g., OpenAI, Anthropic, Google), generates summaries for code files, functions, and classes.
	</Card>
    <Card title="Docstring Indexing & Search">
        The `DocstringIndexer` generates and embeds AI-powered summaries (dynamic docstrings) for code elements. The `SummarySearcher` queries this index for semantic understanding and retrieval based on code intent.
    </Card>
	<Card title="Code Search">
		Includes `CodeSearcher` for literal/regex searches, and `VectorSearcher` for semantic search on raw code embeddings. For semantic search on AI-generated summaries, see "Docstring Indexing & Search".
	</Card>
	<Card title="LLM Context Building">
		`LLMContext` helps in assembling relevant code snippets and information into effective prompts for LLMs.
	</Card>
</CardGrid>

## Planned Enhancements & Future Directions

Here are some areas we're looking to improve and expand upon:

### 1. Enhanced Code Intelligence

*   **`RepoMapper` & Symbol Extraction:**
    *   **Deeper Language Insights:** Beyond basic symbol extraction, explore richer semantic information (e.g., variable types, function signatures in more detail).
    *   **Custom Symbol Types:** Allow users to define and extract custom symbol types relevant to their specific frameworks or DSLs.
    *   **Robustness:** Continue to improve `.gitignore` handling and parsing of various project structures.
    *   **Performance:** Optimize scanning for very large repositories.
*   **`CodeSearcher`:**
    *   **Full File Exclusion:** Implement robust `.gitignore` and other ignore file pattern support.
    *   **Advanced Search Options:** Add features like whole-word matching, and consider more powerful query syntax.
    *   **Performance:** Explore integration with native search tools (e.g., `ripgrep`) as an optional backend for speed.
*   **`VectorSearcher` (Semantic Search):**
    *   **Configurability:** Offer more choices for embedding models, chunking strategies, and vector database backends for raw code embeddings.
    *   **Hybrid Search:** Explore combining keyword and semantic search for optimal results.
    *   **Index Management:** Tools for easier creation, updating, and inspection of semantic search indexes.
*   **Docstring Indexing & Search Enhancements:**
    *   Explore advanced indexing strategies (e.g., hierarchical summaries, metadata filtering for summary search).
    *   Improve management and scalability of summary vector stores.
    *   Investigate hybrid search techniques combining summary semantics with keyword precision.

### 2. Advanced LLM Integration

*   **`Summarizer`:**
    *   **Granular Summaries Refinement:** Refine and expand granular summaries for functions and classes, ensuring broad language construct coverage and exploring different summary depths.
    *   **Multi-LLM Support Expansion:** Expand and standardize multi-LLM support, facilitating easier integration of new cloud providers, local models, and enhancing common configuration interfaces.
    *   **Customizable Prompts:** Allow users more control over the prompts used for summarization.
*   **`LLMContext`:**
    *   **Smarter Context Retrieval:** Develop more sophisticated strategies for selecting the most relevant context for different LLM tasks (e.g., using call graphs, semantic similarity, and historical data).
    *   **Token Optimization:** Implement techniques to maximize information density within LLM token limits.

### 3. Code Transformation & Generation

*   **Refactoring Tools:** Leverage `kit`'s understanding of code to suggest or perform automated refactoring.
*   **Code Generation:** Explore LLM-powered code generation based on existing codebase patterns or natural language descriptions.
*   **Documentation Generation:** Automate the creation or updating of code documentation using `kit`'s analysis and LLM capabilities.

### 4. Broader Language & Framework Support

*   **Tree-sitter Queries:** Continuously expand and refine Tree-sitter queries for robust support across more programming languages and to address specific parsing challenges (e.g., HCL resource extraction noted previously).
*   **Framework Awareness:** Develop extensions or plugins that provide specialized understanding for popular frameworks (e.g., Django, React, Spring).

### 5. Usability & Developer Experience

*   **Comprehensive Testing:** Ensure high test coverage for all modules and functionalities.
*   **Documentation:** Maintain high-quality, up-to-date documentation, including API references, tutorials, and practical recipes.
*   **CLI Development:** Develop a more feature-rich and user-friendly command-line interface for common `kit` operations.
*   ✅ **IDE Integration:** Explore possibilities for integrating `kit`'s features into popular IDEs via plugins, MCP, or Language Server Protocol (LSP) extensions.
*   **REST API Service:** Develop a comprehensive REST API service to make `kit`'s capabilities accessible to non-Python users and applications. This would allow developers using any programming language to leverage `kit`'s code intelligence features through standard HTTP requests.

### 6. Cross-Language & Cross-Platform Support

*   **REST API & Service Layer:** Expand the REST API service to provide comprehensive access to all `kit` features:
    *   **Containerized Deployment:** Provide Docker images and deployment templates for easy self-hosting.
    *   **Client Libraries:** Develop official client libraries for popular languages (TypeScript, Go, Rust) to interact with the `kit` API.
    *   **Authentication & Multi-User Support:** Implement secure authentication and multi-user capabilities for shared deployments.
    *   **Webhooks & Events:** Support webhook integrations for code events and analysis results.

### 7. Community & Extensibility

*   **Plugin Architecture:** Design `kit` with a clear plugin architecture to allow the community to easily add new languages, analysis tools, or LLM integrations.

This roadmap is ambitious, and priorities will be adjusted based on user feedback and development progress.

```

File: /Users/darin/docs/kit/extending/adding-languages.mdx
```mdx
---
title: Adding New Languages
---

- To add a new language:
  1. Add a tree-sitter grammar and build it (see [tree-sitter docs](https://tree-sitter.github.io/tree-sitter/creating-parsers)).
  2. Add a `queries/<lang>/tags.scm` file with queries for symbols you want to extract.
  3. Add the file extension to `TreeSitterSymbolExtractor.LANGUAGES`.
  4. Write/expand tests for the new language.

**Why?**
- This approach lets you support any language with a tree-sitter grammar—no need to change core logic.
- `tags.scm` queries make symbol extraction flexible and community-driven.

```

File: /Users/darin/docs/kit/core-concepts/search-approaches.mdx
```mdx
---
title: Searching
---

Not sure **which `kit` feature to reach for**?  Use this page as a mental map of
search-and-discovery tools – from plain-text grep all the way to LLM-powered
semantic retrieval.

## Decision table

| Your goal | Best tool | One-liner | Docs |
|-----------|-----------|-----------|------|
| Find an exact string or regex | `repo.search_text()` | `repo.search_text("JWT", "*.go")` | [Text search](/docs/core-concepts/semantic-search#exact-keyword) |
| List symbols in a file | `repo.extract_symbols()` | `repo.extract_symbols("src/db.py")` | [Repository API](/docs/core-concepts/repository-api) |
| See where a function is used | `repo.find_symbol_usages()` | `repo.find_symbol_usages("login")` | ^ |
| Get a concise overview of a file / function | `Summarizer` | `summarizer.summarize_file(path)` | [Code summarization](/docs/core-concepts/code-summarization) |
| Semantic search over **raw code chunks** | `VectorSearcher` | `repo.search_semantic()` | [Semantic search](/docs/core-concepts/semantic-search) |
| Semantic search over **LLM summaries** | `DocstringIndexer` + `SummarySearcher` | see below | [Docstring index](/docs/core-concepts/docstring-indexing) |
| Build an LLM prompt with only the *relevant* code | `ContextAssembler` | `assembler.from_chunks(chunks)` | [Context assembly](/docs/core-concepts/context-assembly) |

> **Tip:** You can mix-and-match. For instance, run a docstring search first,
> then feed the matching files into `ContextAssembler` for an LLM chat.

## Approaches in detail

### 1. Plain-text / regex search

Fast, zero-setup, works everywhere. Use when you *know* what string you’re
looking for.

```python
repo.search_text("parse_jwt", file_pattern="*.py")
```

### 2. Symbol indexing

`extract_symbols()` uses **tree-sitter** queries (Python, JS, Go, etc.) to list
functions, classes, variables – handy for nav trees or refactoring tools.

### 3. LLM summarization

Generate natural-language summaries for files, classes, or functions with
`Summarizer`.  Great for onboarding or API docs.

### 4. Vector search (raw code)

`VectorSearcher` chunks code (symbols or lines) → embeds chunks → stores them in
a local vector database.  Good when wording of the query is *similar* to the
code.

### 5. Docstring vector search

`DocstringIndexer` first *summarizes* code, then embeds the summary.  The
resulting vectors capture **intent**, not syntax; queries like “retry back-off
logic” match even if the code uses exponential delays without those words.

---

Still unsure?  Start with text-search (cheap), move to vector search (smart),
and layer summaries when you need *meaning* over *matching*.

```

File: /Users/darin/docs/kit/introduction/overview.mdx
```mdx
---
title: Overview
---

## kit: Code Intelligence Toolkit

A modular, production-grade toolkit for codebase mapping, symbol extraction, code search, and LLM-powered developer workflows. Supports multi-language codebases via `tree-sitter`.

`kit` features a "mid-level API" to build your own custom tools, applications, agents, and workflows: easily build code review bots, semantic code search, documentation generators, and more.

`kit` is **free and open source** with a permissive MIT license. Check it out on [GitHub](https://github.com/cased/kit).

## Installation
### Install from PyPI
```bash
# Basic installation, it's currently `cased-kit` on pypi
pip install cased-kit
```

### Install from Source
```bash
git clone https://github.com/cased/kit.git
cd kit
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

## Why Use kit?

`kit` helps with:

*   **Unifying Code Access:** Provides a single, consistent `Repository` object to interact with files, symbols, and search across diverse codebases, regardless of language.
*   **Deep Code Understanding:** Leverages `tree-sitter` for accurate, language-specific parsing, enabling reliable symbol extraction and structural analysis across an entire codebase.
*   **Bridging Code and LLMs:** Offers tools specifically designed to chunk code effectively and retrieve relevant context for large language models, powering smarter AI developer tools.

## Core Philosophy

`kit` aims to be a **toolkit** for building applications, agents, and workflows.
It handles the low-level parsing and indexing complexity, and allows you to adapt these components to your specific needs.

We believe the building blocks for code intelligence and LLM workflows for developer tools should be free and open source,
so you can build amazing products and experiences.


## Where to Go Next

*   **Dive into the API:** Explore the [Core Concepts](/core-concepts/repository-api) to understand the `Repository` object and its capabilities.
*   **Build Something:** Follow the [Tutorials](/tutorials/ai_pr_reviewer) for step-by-step guides on creating practical tools.

## LLM Documentation

This documentation site provides generated text files suitable for LLM consumption:

- [`/llms.txt`](/llms.txt): Entrypoint file following the llms.txt standard.
- [`/llms-full.txt`](/llms-full.txt): Complete documentation content concatenated into a single file.
- [`/llms-small.txt`](/llms-small.txt): Minified documentation content for models with smaller context windows.

```

File: /Users/darin/docs/kit/tutorials/codebase_summarizer.mdx
```mdx
---
title: Codebase Summarizer
---

This tutorial shows how to use `kit` to generate a structured Markdown summary of your codebase, including the file tree and all extracted symbols (functions, classes, etc.). Such a summary can be invaluable for quickly understanding a new project, tracking architectural changes, or for documentation purposes.

## Step 1: Summarize the Codebase Structure

The core of this task lies in using `kit`'s `Repository` object to analyze the codebase and extract its structural information. This process involves two main `kit` operations:

1.  **Initializing the `Repository`**: `repo = Repository(repo_path)` creates an instance that points `kit` to the target codebase. `kit` then becomes aware of the repository's location and is ready to perform various analyses.
2.  **Indexing the Repository**: `index = repo.index()` is a key `kit` command. When called, `kit` (typically using its internal `RepoMapper` component) traverses the repository, parses supported source files, identifies structural elements like files, directories, classes, functions, and other symbols. It then compiles this information into a structured `index`.

Use kit's `Repo` object to index the codebase and gather all relevant information.

```python
from kit import Repository

def summarize_codebase(repo_path: str) -> str:
    repo = Repository(repo_path)
    index = repo.index()
    lines = [f"# Codebase Summary for {repo_path}\n"]
    lines.append("## File Tree\n")
    # The index['file_tree'] contains a list of file and directory paths
    for file_info in index["file_tree"]:
        # Assuming file_info is a dictionary or string representing the path
        # Adjust formatting based on the actual structure of file_info objects from repo.index()
        if isinstance(file_info, dict):
            lines.append(f"- {file_info.get('path', file_info.get('name', 'Unknown file/dir'))}")
        else:
            lines.append(f"- {file_info}") # Fallback if it's just a string path

    lines.append("\n## Symbols\n")
    # The index['symbols'] is typically a dictionary where keys are file paths
    # and values are lists of symbol information dictionaries for that file.
    for file_path, symbols_in_file in index["symbols"].items():
        lines.append(f"### {file_path}")
        for symbol in symbols_in_file:
            # Each symbol dict contains details like 'type' (e.g., 'function', 'class') and 'name'.
            lines.append(f"- **{symbol['type']}** `{symbol['name']}`")
        lines.append("")
    return "\n".join(lines)
```

This function, `summarize_codebase`, first initializes `kit` for the given `repo_path`. Then, `repo.index()` does the heavy lifting of analyzing the code. The resulting `index` object is a dictionary, typically containing at least two keys:

*   `'file_tree'`: A list representing the directory structure and files within the repository.
*   `'symbols'`: A dictionary where keys are file paths, and each value is a list of symbols found in that file. Each symbol is itself a dictionary containing details like its name and type (e.g., function, class).

The rest of the function iterates through this structured data to format it into a human-readable Markdown string.

---

## Step 2: Command-Line Interface

To make the summarizer easy to use from the terminal, we'll add a simple command-line interface using Python's `argparse` module. This allows the user to specify the repository path and an optional output file for the summary.

Provide CLI arguments for repo path and output file:

```python
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="Codebase summarizer using kit.")
    parser.add_argument("--repo", required=True, help="Path to the code repository")
    parser.add_argument("--output", help="Output Markdown file (default: stdout)")
    args = parser.parse_args()
    summary = summarize_codebase(args.repo)
    if args.output:
        with open(args.output, "w") as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    else:
        print(summary)

if __name__ == "__main__":
    main()
```

---

## Step 3: Running the Script

With the script in place, you can execute it from your terminal. You'll need to provide the path to the repository you want to summarize and, optionally, a path where the Markdown output file should be saved. If no output file is specified, the summary will be printed to the console.

Run the summarizer like this:

```sh
python codebase_summarizer.py --repo /path/to/repo --output summary.md
```

---

## Example Output

The generated Markdown file (or console output) will provide a clear, structured overview of your project, derived directly from `kit`'s analysis. It will list the files and then, for each file, the symbols defined within it.

```
# Codebase Summary for /path/to/repo

## File Tree
- main.py
- utils.py
- models/
- models/model.py

## Symbols
### main.py
- **function** `main`
- **class** `App`

### utils.py
- **function** `helper`
```

```

File: /Users/darin/docs/kit/tutorials/ai_pr_reviewer.mdx
```mdx
---
title: Build an AI PR Reviewer
---

import { Aside } from '@astrojs/starlight/components';

`kit` shines when an LLM needs to *understand a change in the context of the **entire** code-base*—exactly what a human reviewer does. 
A good review often requires looking beyond the immediate lines changed to understand their implications, check for consistency with existing patterns, and ensure no unintended side-effects arise. This tutorial walks through a **minimal but complete** AI PR-review bot that demonstrates how `kit` provides this crucial whole-repo context.

1.  Fetches a GitHub PR (diff + metadata).
2.  Builds a `kit.Repository` for the **changed branch** so we can query *any* file, symbol or dependency as it exists in that PR.
3.  Generates a focused context bundle with `kit.llm_context.ContextAssembler`, which intelligently combines the diff, the full content of changed files, relevant neighboring code, and even semantically similar code from elsewhere in the repository.
4.  Sends the bundle to an LLM and posts the comments back to GitHub.

By the end you will see how a few dozen lines of Python—plus `kit`—give your LLM the *whole-repo* superpowers, enabling it to perform more insightful and human-like code reviews.

## 1. Fetch PR data

To start, our AI reviewer needs the raw materials of the pull request. 

Use the GitHub REST API to grab the *diff* **and** the PR-head **commit SHA**:

```python
import os, requests

def fetch_pr(repo, pr_number):
    """Return the PR's unified diff **and** head commit SHA."""
    token = os.getenv("GITHUB_TOKEN")
    url   = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    # 1) Unified diff
    diff_resp = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github.v3.diff",
            "Authorization": f"token {token}",
        },
        timeout=15,
    )
    diff_resp.raise_for_status()
    diff = diff_resp.text

    # 2) JSON metadata (for head SHA, title, description, …)
    meta_resp = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {token}",
        },
        timeout=15,
    )
    meta_resp.raise_for_status()
    pr_info = meta_resp.json()

    head_sha = pr_info["head"]["sha"]
    return diff, head_sha
```

---
## 2. Create a `Repository` for the PR branch

With the `head_sha` obtained, we **ideally** want to load the repository *at that exact commit*.  Today, `kit.Repository` will clone the **default branch** of a remote repository (usually `main`) when you pass a URL.  If you need the precise PR-head commit you have two options:

1. Clone the repo yourself, `git checkout <head_sha>`, and then point `Repository` at that local path.
2. Call `Repository(url)` to fetch the default branch **and** apply the PR diff in memory (as we do later in this tutorial).  For many review tasks this is sufficient because the changed files still exist on `main`, and the diff contains the exact edits.

Direct `ref=`/commit checkout support is coming shortly.

So for now we'll simply clone the default branch and rely on the diff for any code that hasn't been pushed upstream:

```python
from kit import Repository

repo = Repository(
    path_or_url="https://github.com/OWNER/REPO.git", # Replace with actual repo URL
    github_token=os.getenv("GITHUB_TOKEN"),
    cache_dir="~/.cache/kit",  # clones are cached for speed
)
```

The `cache_dir` parameter tells `kit` where to store parts of remote repositories it fetches. 
This caching significantly speeds up subsequent operations on the same repository or commit, which is very beneficial for a bot that might process multiple PRs or re-analyze a PR if it's updated.

Now `repo` can *instantly* answer questions like:
`repo.search_text("TODO")` (useful for checking if the PR resolves or introduces to-do items),
`repo.extract_symbols('src/foo.py')` (to understand the structure of a changed file),
`repo.find_symbol_usages('User')` (to see how a modified class or function is used elsewhere, helping to assess the impact of changes).
These capabilities allow our AI reviewer to gather rich contextual information far beyond the simple diff.

---
## 3. Build context for the LLM

The `ContextAssembler` is the workhorse for preparing the input to the LLM. It orchestrates several `kit` features to build a comprehensive understanding of the PR:

```python
from kit import Repository
from unidiff import PatchSet
from sentence_transformers import SentenceTransformer

# Assume `repo`, `diff`, `pr_title`, `pr_description` are defined
# `diff` is the raw diff string
# `pr_title`, `pr_description` are strings from your PR metadata

# -------------------------------------------------
# 1) Build or load the semantic index so search_semantic works
# -------------------------------------------------
st_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_fn = lambda text: st_model.encode(text).tolist()

vs = repo.get_vector_searcher(embed_fn)
vs.build_index()  # do this once; subsequent runs can skip if cached

# -------------------------------------------------
# 2) Assemble context for the LLM
# -------------------------------------------------
assembler = repo.get_context_assembler()
patch = PatchSet(diff)

# Add the raw diff
assembler.add_diff(diff)

# Add full content of changed / added files – with safety guards
LOCK_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    "composer.lock",
}

for p_file in patch:
    if p_file.is_removed_file:
        continue  # nothing to embed

    assembler.add_file(
        p_file.path,
        max_lines=400,              # Inline only if the file is reasonably small
        skip_if_name_in=LOCK_FILES, # Skip bulky lock files entirely (diff already added)
    )

# Semantic search for related code using PR title/description
for q in filter(None, [pr_title, pr_description]):
    q = q.strip()
    if not q:
        continue
    hits = repo.search_semantic(q, top_k=3, embed_fn=embed_fn)
    assembler.add_search_results(hits, query=f"Code semantically related to: '{q}'")

context_blob = assembler.format_context()
```

The `ContextAssembler` is used as follows:

1.  **`assembler.add_diff(diff)`**: This provides the LLM with the direct changes from the PR.
2.  **`assembler.add_file(p_file.path)`**: Supplying the full content of changed files allows the LLM to see modifications in their complete original context, not just the diff hunks.
3.  **Augment with Semantic Search (`assembler.add_search_results(...)`)**: This is a key step where `kit` truly empowers the AI reviewer. Beyond direct code connections, `kit`'s `repo.search_semantic()` method can unearth other code sections that are *conceptually related* to the PR's intent, even if not directly linked by calls or imports.

    You can use queries derived from the PR's title or description to find examples of similar functionality, relevant design patterns, or areas that might require parallel updates.

    **The Power of Summaries**: While `repo.search_semantic()` can operate on raw code, its effectiveness is significantly amplified when your `Repository` instance is configured with a `DocstringIndexer`. The `DocstringIndexer` (see the [Docstring Search Tutorial](/tutorials/docstring_search)) preprocesses your codebase, generating AI summaries for files or symbols. When `repo.search_semantic()` leverages this index, it matches based on the *meaning and purpose* captured in these summaries, leading to far more relevant and insightful results than simple keyword or raw-code vector matching. This allows the AI reviewer to understand context like "find other places where we handle user authentication" even if the exact phrasing or code structure varies.

    The Python code snippet above illustrates how you might integrate this. Remember to ensure your `repo` object is properly set up with an embedding function and, for best results, a `DocstringIndexer`. Refer to the "[Docstring Search](/tutorials/docstring_search)" and "[Semantic Code Search](/tutorials/semantic_code_search)" tutorials for detailed setup guidance.

Finally, `assembler.format_context()` consolidates all the added information into a single string (`context_blob`), ready to be sent to the LLM. This step might also involve applying truncation or specific formatting to optimise for the LLM's input requirements.

---
## 4. Prepare the LLM Prompt

With the meticulously assembled `context_blob` from `kit`, we can now prompt an LLM. The quality of the prompt—including the system message that sets the LLM's role and the user message containing the context—is vital. Because `kit` has provided such comprehensive and well-structured context, the LLM is significantly better equipped to act like an "expert software engineer" and provide a nuanced, insightful review.

```python
from openai import OpenAI

client = OpenAI()
msg = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are an expert software engineer …"},
        {"role": "user",   "content": f"PR context:\n```\n{context_blob}\n```\nGive a review."},
    ],
)
review = msg.choices[0].message.content.strip()
```

---
## 5. Post the review back to GitHub

This final step completes the loop by taking the LLM's generated review and posting it as a comment on the GitHub pull request. This delivers the AI's insights directly to the developers, integrating the AI reviewer into the existing development workflow.

```python
requests.post(
    f"https://api.github.com/repos/{repo_full}/issues/{pr_number}/comments",
    headers={
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
    },
    json={"body": review},
    timeout=10,
).raise_for_status()
```

---
## Where to go next?

This tutorial provides a foundational AI PR reviewer. `kit`'s components can help you extend it further:

* **Chunk large diffs or files** – If a PR is very large, the `ContextAssembler` currently adds full content. You might need strategies to chunk very large files (e.g. `repo.chunk_file_by_symbols`) or diffs, or implement more granular context addition to stay within LLM limits.
* **Custom ranking** – The `ContextAssembler` could be configured or extended to allow different weights for various context pieces (e.g. prioritising semantic-search matches that are highly relevant over less critical information). `kit`'s search results, which include scores, can inform this process.
* **Inline comments** – Parse the LLM's output to identify suggestions pertaining to specific files and lines, then use GitHub's *review* API to post comments directly on the diff. `kit`'s symbol mapping (line numbers from `RepoMapper`) is crucial here.
* **Supersonic** – For more advanced automation, tools like Supersonic could leverage `kit`'s understanding to not just *suggest* but also *apply* LLM-recommended changes, potentially opening follow-up PRs.

> With `kit` your LLM sees code the way *humans* do: in the rich context of the entire repository. Better signal in → better reviews out.

```

File: /Users/darin/docs/kit/introduction/usage-guide.mdx
```mdx
---
title: Usage Guide
---

This guide provides practical examples of how to use the core `Repository` object in `kit` to interact with your codebase.

## Initializing a `Repository`

First, create an instance of the `Repository` class, pointing it to your code. `kit` can work with local directories or clone remote Git repositories.
This is the starting point for any analysis, giving `kit` access to the codebase.

### Local Directory

If your code is already on your machine:

```python
from kit import Repository

repo = Repository("/path/to/your/local/project")
```

### Remote Git Repository

`kit` can clone a public or private Git repository. For private repos, provide a GitHub token.

```python
# Public repo
repo = Repository("https://github.com/owner/repo-name")

# Private repo (requires token)
# Ensure the token has appropriate permissions
github_token = "your_github_pat_here"
repo = Repository("https://github.com/owner/private-repo-name", github_token=github_token)
```

### Caching

When cloning remote repositories, `kit` caches them locally to speed up subsequent initializations. By default, caches are stored in a temporary directory. You can specify a persistent cache directory:

```python
repo = Repository(
    "https://github.com/owner/repo-name", 
    cache_dir="/path/to/persistent/cache"
)
```

## Basic Exploration

Once initialized, you can explore the codebase.
Use these methods to get a high-level overview of the repository's structure and key code elements, or to gather foundational context for an LLM.

### Getting the File Tree

List all files and directories:

```python
file_tree = repo.get_file_tree()
# Returns a list of dicts: [{'path': '...', 'is_dir': False, ...}, ...]
```

### Extracting Symbols

Identify functions, classes, etc., across the whole repo or in a specific file:

```python
# All symbols
all_symbols = repo.extract_symbols()

# Symbols in a specific file
specific_symbols = repo.extract_symbols("src/my_module.py")
# Returns a list of dicts: [{'name': '...', 'type': 'function', ...}, ...]
```

### Searching Text

Perform simple text or regex searches:

```python
matches = repo.search_text("my_function_call", file_pattern="*.py")
# Returns a list of dicts: [{'file': '...', 'line_number': 10, ...}, ...]
```

## Preparing Code for LLMs

`kit` provides utilities to prepare code snippets for large language models.
These methods help break down large codebases into manageable pieces suitable for LLM context windows or specific analysis tasks.

### Chunking

Split files into manageable chunks, either by line count or by symbol definition:

```python
# Chunk by lines
line_chunks = repo.chunk_file_by_lines("src/long_file.py", max_lines=100)

# Chunk by symbols (functions, classes)
symbol_chunks = repo.chunk_file_by_symbols("src/long_file.py")
```

### Extracting Context

Get the specific function or class definition surrounding a given line number:

```python
context = repo.extract_context_around_line("src/my_module.py", line=42)
# Returns a dict like {'name': 'my_function', 'type': 'function', 'code': 'def my_function(...): ...'}
```

## Generating Code Summaries (Alpha)


`kit` includes an alpha feature for generating natural language summaries (like dynamic docstrings) for code elements (files, functions, classes) using a configured Large Language Model (LLM). This can be useful for:

*   Quickly understanding the purpose of a piece of code.
*   Providing context to other LLM-powered tools.
*   Powering semantic search based on generated summaries rather than just raw code.

**Note:** This feature is currently in **alpha**. The API may change, and it requires an LLM (e.g., via OpenAI, Anthropic) to be configured for `kit` to use for summarization.

### Using the `DocstringIndexer`

The `DocstringIndexer` is responsible for managing the summarization process and storing/retrieving these generated "docstrings."

```python
from kit import Repository
from kit.docstring_indexer import DocstringIndexer
from kit.summaries import Summarizer, OpenAIConfig
from sentence_transformers import SentenceTransformer  # or any embedder of your choice

# 1. Initialize your Repository
repo = Repository("tests/fixtures/realistic_repo")  # Or your project path

# 2. Configure the LLM-powered summarizer
# Make sure the relevant API key (e.g., OPENAI_API_KEY) is set in your environment
summarizer = Summarizer(repo, OpenAIConfig(model="gpt-4o"))

# 3. Provide an embedding function (str -> list[float]) for the vector index
st_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_fn = lambda text: st_model.encode(text).tolist()

# 4. Create the DocstringIndexer
#    You can specify where on disk to persist the vector DB via `persist_dir`.
indexer = DocstringIndexer(
    repo,
    summarizer,
    embed_fn,
    persist_dir="kit_docstring_cache",
)

# 5. Build the index (generates summaries for new/changed files/symbols)
#    This may take some time depending on repository size and LLM speed.
indexer.build(force=True)  # `level="symbol"` by default

# 6. Retrieve a summary – use the built-in SummarySearcher
searcher = indexer.get_searcher()
hits = searcher.search("utils.greet", top_k=1)  # Search by symbol or natural language
if hits:
    print("Summary:", hits[0]["summary"])
else:
    print("No summary found (yet).")
```

This generated summary can then be used for various purposes, including enhancing semantic search or providing contextual information for code generation tasks. Refer to the [Core Concepts: Docstring Indexing](/core-concepts/docstring-indexing) page for more details on configuration and advanced usage.

## Semantic Code Search

Perform vector-based semantic search (requires configuration).
Go beyond keyword search to find code related by meaning or concept, useful for discovery and understanding.

```python
# NOTE: Requires prior setup - see Core Concepts > Configuring Semantic Search
results = repo.search_semantic("find code related to database connections", top_k=3)
```

(See [Configuring Semantic Search](/core-concepts/configuring-semantic-search) for setup details.)

## Finding Symbol Usages

Locate all definitions and references of a specific symbol:
Track down where functions or classes are defined and used throughout the codebase for impact analysis or refactoring.

```python
usages = repo.find_symbol_usages("MyClass", symbol_type="class")
# Returns a list of dicts showing definitions and text matches across the repo.
```

## Exporting Data

`kit` can export the gathered information (file tree, symbols, index, usages) to JSON files for use in other tools or offline analysis.
Persist the results of your analysis or integrate `kit`'s findings into other development workflows.

```python
# Export the full index (files + symbols)
repo.write_index("repo_index.json")

# Export only symbols
repo.write_symbols("symbols.json")

# Export file tree
repo.write_file_tree("file_tree.json")

# Export usages of a symbol
repo.write_symbol_usages("MyClass", "my_class_usages.json", symbol_type="class")

```

```

File: /Users/darin/docs/kit/tutorials/dependency_graph_visualizer.mdx
```mdx
---
title: Dependency Graph Visualizer in Python
---

import { Aside } from '@astrojs/starlight/components';

This tutorial demonstrates how to visualize the dependency graph of a codebase using `kit`. `kit`'s `DependencyAnalyzer` supports analyzing dependencies in both Python and Terraform codebases, and can output the graph in DOT format, which you can render with Graphviz to generate visual diagrams.

For Python codebases, the analyzer leverages Abstract Syntax Tree (AST) parsing to track import relationships between modules. For Terraform codebases, it analyzes resource references and dependencies between infrastructure components.

<Aside type="note">
  To directly generate an image (e.g., PNG, SVG) without manually handling DOT files, you can use the `analyzer.visualize_dependencies()` method, provided you have both the `graphviz` Python package and the Graphviz system executables installed.
</Aside>

## Step 1: Generate the Dependency Graph in DOT Format

The `kit.Repository` object provides access to a `DependencyAnalyzer` which can build and export the dependency graph.

```python
from kit import Repository

def generate_dot_dependency_graph(repo_path: str) -> str:
    """
    Initializes a Repository, gets its DependencyAnalyzer,
    and exports the dependency graph in DOT format.
    """
    repo = Repository(repo_path)
    # Specify the language ('python' or 'terraform')
    analyzer = repo.get_dependency_analyzer('python')
    
    # The build_dependency_graph() method is called implicitly by export_dependency_graph
    # if the graph hasn't been built yet.
    dot_output = analyzer.export_dependency_graph(output_format='dot')
    
    # Ensure dot_output is a string. export_dependency_graph returns the content 
    # when output_path is None.
    if not isinstance(dot_output, str):
        # This case should ideally not happen if output_format='dot' and output_path=None
        # based on typical implementations, but good to be defensive.
        raise TypeError(f"Expected DOT output as string, got {type(dot_output)}")

    return dot_output
```

This function `generate_dot_dependency_graph`:
1. Initializes the `Repository` for the given `repo_path`.
2. Gets a `DependencyAnalyzer` instance from the repository.
3. Calls `analyzer.export_dependency_graph(output_format='dot')` to get the graph data as a DOT formatted string.

## Step 2: Command-Line Interface

Add CLI arguments for the repository path and an optional output file for the DOT content.

```python
import argparse

# Assume generate_dot_dependency_graph function from Step 1 is defined above

def main() -> None:
    parser = argparse.ArgumentParser(description="Dependency graph visualizer using kit.")
    parser.add_argument("--repo", required=True, help="Path to the code repository")
    parser.add_argument("--output", help="Output DOT file (default: stdout)")
    args = parser.parse_args()
    
    try:
        dot_content = generate_dot_dependency_graph(args.repo)
        if args.output:
            with open(args.output, "w") as f:
                f.write(dot_content)
            print(f"Dependency graph (DOT format) written to {args.output}")
        else:
            print(dot_content)
    except Exception as e:
        print(f"An error occurred: {e}")
        # For more detailed debugging, you might want to print the traceback
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    main()
```

## Step 3: Running the Script

Run the visualizer script from your terminal. Provide the path to the repository and optionally an output file name for the DOT data.

```sh
python your_script_name.py --repo /path/to/your/python_project --output project_deps.dot
```

Replace `your_script_name.py` with the actual name of your Python file containing the code from Steps 1 and 2.

## Step 4: Rendering the Graph

To visualize the generated DOT file, you need Graphviz installed on your system. Use the `dot` command-line tool:

```sh
dot -Tpng project_deps.dot -o project_deps.png
```

This will create a PNG image (`project_deps.png`) of your codebase's import relationships.

## Extending the Visualizer

`kit`'s `DependencyAnalyzer` offers more than just DOT export:

- **Direct Visualization**: Use `analyzer.visualize_dependencies(output_path="graph_image_prefix", format="png")` to directly save an image (requires the `graphviz` Python library).
- **Other Export Formats**: Export to JSON, GraphML, or an adjacency list using `analyzer.export_dependency_graph(output_format=...)`.
- **Cycle Detection**: Use `analyzer.find_cycles()` to identify circular dependencies.
- **Querying the Graph**: 
  - For Python: Use `analyzer.get_module_dependencies()` and `analyzer.get_dependents()` to explore module relationships.
  - For Terraform: Use `analyzer.get_resource_dependencies()` and `analyzer.get_resource_by_type()` to explore infrastructure dependencies.
- **Reports and Context**: 
  - Generate a comprehensive JSON report with `analyzer.generate_dependency_report()`.
  - Create LLM-friendly context with `analyzer.generate_llm_context()`.
- **File Paths**: The analyzer tracks absolute file paths for each component, making it easy to locate resources in complex projects.

## Using with Terraform

To analyze a Terraform codebase instead of Python, simply specify 'terraform' when getting the analyzer:

```python
analyzer = repo.get_dependency_analyzer('terraform')
```

The Terraform analyzer will map dependencies between resources, modules, variables, and other Terraform components. All resources in the graph include their absolute file paths, making it easy to locate them in complex infrastructure projects with files that might have the same name in different directories.

## Conclusion

Visualizing dependencies helps you understand, refactor, and document complex codebases. With `kit`'s `DependencyAnalyzer` and tools like Graphviz, you can gain valuable insights into your project's structure, whether it's a Python application or Terraform infrastructure.

```

File: /Users/darin/docs/kit/introduction/quickstart.mdx
```mdx
---
title: Quickstart
---

```bash
git clone https://github.com/cased/kit.git
cd kit
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

Now, you can use kit!
kit ships with a demonstration repository at `tests/fixtures/` you can use to get started. 

Try this simple Python script (e.g., save as `test_kit.py` in the `kit` directory you cloned):

```python
import kit
import os

# Path to the demo repository
repo_path = "tests/fixtures/realistic_repo"

print(f"Loading repository at: {repo_path}")
# Ensure you have cloned the 'kit' repository and are in its root directory
# for this relative path to work correctly.
repo = kit.Repository(repo_path)

# Print the first 5 Python files found in the demo repo
print("\nFound Python files in the demo repo (first 5):")
count = 0
for file in repo.files('*.py'):
    print(f"- {file.path}")
    count += 1
    if count >= 5:
        break

if count == 0:
    print("No Python files found in the demo repository.")

# Extract symbols from a specific file in the demo repo (e.g., app.py)
target_file = 'app.py'
print(f"\nExtracting symbols from {target_file} in the demo repo (first 5):")
try:
    symbols = repo.extract_symbols(target_file)
    if symbols:
        for i, symbol in enumerate(symbols):
            print(f"- {symbol.name} ({symbol.kind}) at line {symbol.range.start.line}")
            if i >= 4:
                break
    else:
        print(f"No symbols found or file not parseable: {target_file}")
except FileNotFoundError:
    print(f"File not found: {target_file}")
except Exception as e:
    print(f"An error occurred extracting symbols: {e}")

```

Run it with `python test_kit.py`.

Next, explore the [Usage Guide](/introduction/usage-guide) to understand the core concepts.

```

File: /Users/darin/docs/kit/tutorials/dump_repo_map.mdx
```mdx
---
title: Dump Repo Map
---

import { Aside } from '@astrojs/starlight/components';

This tutorial explains how to use `kit` to dump a complete map of your repository—including the file tree and all extracted symbols—as a JSON file. This is useful for further analysis, visualization, or integration with other tools. `kit` provides a convenient method on the `Repository` object to achieve this directly.

## Step 1: Create the Script

Create a Python script named `dump_repo_map.py` with the following content. This script uses `argparse` to accept the repository path and the desired output file path.

```python
# dump_repo_map.py
from kit import Repository # Import the main Repository class
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Dump a repository's file tree and symbols as JSON using kit.")
    parser.add_argument("repo_path", help="Path to the repository directory.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    args = parser.parse_args()

    repo_path = args.repo_path
    if not os.path.isdir(repo_path):
        print(f"Error: Repository path not found or not a directory: {repo_path}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Initializing repository at: {repo_path}", file=sys.stderr)
        repo = Repository(repo_path)
        
        print(f"Dumping repository index to: {args.output_file}", file=sys.stderr)
        repo.write_index(args.output_file) # Use the direct method
        
        print(f"Successfully wrote repository map to {args.output_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error processing repository: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Step 2: Run the Script

Save the code above as `dump_repo_map.py`. You can then run it from your terminal, providing the path to the repository you want to map and the desired output file name:

```sh
python dump_repo_map.py /path/to/repo repo_map.json
```

This will create a JSON file (e.g., `repo_map.json`) containing the structure and symbols of your codebase.

---

## Example JSON Output

The output JSON file will contain a `file_tree` (also aliased as `files`) and a `symbols` map.

```json
{
  "file_tree": [
    {
      "path": "src",
      "is_dir": true,
      "name": "src",
      "size": 0
    },
    {
      "path": "src/main.py",
      "is_dir": false,
      "name": "main.py",
      "size": 1024
    },
    {
      "path": "README.md",
      "is_dir": false,
      "name": "README.md",
      "size": 2048
    }
    // ... more files and directories
  ],
  "files": [
    // ... same content as file_tree ...
  ],
  "symbols": {
    "src/main.py": [
      {
        "type": "function", 
        "name": "main", 
        "start_line": 10, 
        "end_line": 25, 
        "code": "def main():\n  pass"
      },
      {
        "type": "class", 
        "name": "App", 
        "start_line": 30, 
        "end_line": 55
      }
    ],
    "src/utils.py": [
      {
        "type": "function", 
        "name": "helper", 
        "start_line": 5, 
        "end_line": 12
      }
    ]
    // ... more files and their symbols
  }
}
```

<Aside type="note">
  The exact content and structure of symbol information (e.g., inclusion of `code` snippets) depends on the `RepoMapper`'s symbol extraction capabilities for the specific languages in your repository.
</Aside>

---

## Integration Ideas

- Use the JSON output to feed custom dashboards or documentation tools.
- Integrate with code search or visualization tools.
- Use for code audits, onboarding, or automated reporting.

---

## Conclusion

With `kit`, you can easily export a structured map of your repository using `repo.write_index()`, making this data readily available for various downstream use cases and custom tooling.

```

File: /Users/darin/docs/kit/tutorials/codebase-qa-bot.mdx
```mdx
---
title: Codebase Q&A Bot with Summaries
---

import { Steps } from '@astrojs/starlight/components';

This tutorial demonstrates how to build a simple question-answering bot for your codebase. The bot will:

1.  Use `DocstringIndexer` to create semantic summaries of each file.
2.  When a user asks a question, use `SummarySearcher` to find relevant file summaries.
3.  Fetch the full code of those top files.
4.  Use `ContextAssembler` to build a concise prompt for an LLM.
5.  Get an answer from the LLM.

This approach is powerful because it combines semantic understanding (from summaries) with the full detail of the source code, allowing an LLM to answer nuanced questions.

## Prerequisites

*   You have `kit` installed (`pip install cased-kit`).
*   You have an OpenAI API key set (`export OPENAI_API_KEY=...`).
*   You have a local Git repository you want to query.

## Steps

<Steps>

1.  **Initialize Components**

    First, let's set up our `Repository`, `DocstringIndexer`, `Summarizer` (for the indexer), `SummarySearcher`, and `ContextAssembler`.

    ```python
    from kit import Repository, DocstringIndexer, Summarizer, SummarySearcher, ContextAssembler
    from kit.summaries import OpenAIConfig 

    # --- Configuration ---
    REPO_PATH = "/path/to/your/local/git/repo" #! MODIFY
    # For DocstringIndexer, persist_dir is where the DB is stored.
    # Let's use a directory for ChromaDB as it might create multiple files.
    INDEX_PERSIST_DIR = "./my_code_qa_index_db/" 

    # Use a specific summarizer model for indexing, can be different from Q&A LLM
    INDEXER_LLM_CONFIG = OpenAIConfig(model="gpt-4o")

    # LLM for answering the question based on context
    QA_LLM_CONFIG = OpenAIConfig(model="gpt-4o") # Or your preferred model
    # MAX_CONTEXT_CHARS is not directly used by ContextAssembler in this simplified flow
    # TOP_K_SUMMARIES = 3 remains relevant for SummarySearcher
    TOP_K_SUMMARIES = 3 
    # --- END Configuration ---

    repo = Repository(REPO_PATH)

    # For DocstringIndexer - requires repo and a summarizer instance
    summarizer_for_indexing = Summarizer(repo=repo, config=INDEXER_LLM_CONFIG) 
    indexer = DocstringIndexer(repo, summarizer_for_indexing, persist_dir=INDEX_PERSIST_DIR)

    # For SummarySearcher - get it from the indexer
    searcher = indexer.get_searcher()

    # For assembling context for the Q&A LLM
    assembler = ContextAssembler(repo)

    # We'll need an LLM client to ask the final question
    qa_llm_client = Summarizer(repo=repo, config=QA_LLM_CONFIG)._get_llm_client()
    print("Components initialized.")
    ```

    Make sure to replace `"/path/to/your/local/git/repo"` with the actual path to your repository.
    Also ensure the directory for `INDEX_PERSIST_DIR` (e.g., `my_code_qa_index_db/`) can be created.

2.  **Build or Load the Index**

    The `DocstringIndexer` needs to process your repository to create summaries and embed them. This can take time for large repositories. We'll check if an index already exists and build it if not.

    ```python
    import os

    # Check based on persist_dir for the indexer
    if not os.path.exists(INDEX_PERSIST_DIR) or not any(os.scandir(INDEX_PERSIST_DIR)):
        print(f"Index not found or empty at {INDEX_PERSIST_DIR}. Building...")
        # Build a symbol-level index for more granular results
        # force=True will rebuild if the directory exists but is perhaps from an old run
        indexer.build(level="symbol", file_extensions=[".py", ".js", ".md"], force=True)
        print("Symbol-level index built successfully.")
    else:
        print(f"Found existing index at {INDEX_PERSIST_DIR}.")
    ```

3.  **Define the Question-Answering Function**

    This function will orchestrate the search, context assembly, and LLM query.

    ```python
    def answer_question(user_query: str) -> str:
        print(f"\nSearching for files/symbols relevant to: '{user_query}'")
        # 1. Search for relevant file/symbol summaries
        search_results = searcher.search(user_query, top_k=TOP_K_SUMMARIES)

        if not search_results:
            return "I couldn't find any relevant files or symbols in the codebase to answer your question."

        print(f"Found {len(search_results)} relevant document summaries.")
        # Reset assembler for each new question to start with fresh context
        current_question_assembler = ContextAssembler(repo)

        # 2. Add relevant context to the assembler
        added_content_identifiers = set() # To avoid adding the same file multiple times if symbols from it are retrieved

        for i, res in enumerate(search_results):
            file_path = res.get('file_path')
            identifier_for_log = file_path
            
            if res.get('level') == 'symbol':
                symbol_name = res.get('symbol_name', 'Unknown Symbol')
                symbol_type = res.get('symbol_type', 'Unknown Type')
                identifier_for_log = f"Symbol: {symbol_name} in {file_path} (Type: {symbol_type})"
            
            print(f"  {i+1}. {identifier_for_log} (Score: {res.get('score', 0.0):.4f})")

            # For simplicity, add the full file content for any relevant file found,
            # whether the hit was file-level or symbol-level.
            # A more advanced version could add specific symbol code using a custom method.
            if file_path and file_path not in added_content_identifiers:
                try:
                    # Add full file content for context
                    current_question_assembler.add_file(file_path)
                    added_content_identifiers.add(file_path)
                    print(f"    Added content of {file_path} to context.")
                except FileNotFoundError:
                    print(f"    Warning: File {file_path} not found when trying to add to context.")
                except Exception as e:
                    print(f"    Warning: Error adding {file_path} to context: {e}")
        
        if not added_content_identifiers:
             return "Found relevant file/symbol names, but could not retrieve their content for context."

        # 3. Get the assembled context string
        prompt_context = current_question_assembler.format_context()
        
        if not prompt_context.strip():
            return "Could not assemble any context for the LLM based on search results."

        # 4. Formulate the prompt and ask the LLM
        system_message = (
            "You are a helpful AI assistant with expertise in the provided codebase. "
            "Answer the user's question based *only* on the following code context. "
            "If the answer is not found in the context, say so. Be concise."
        )
        final_prompt = f"## Code Context:\n\n{prompt_context}\n\n## User Question:\n\n{user_query}\n\n## Answer:"

        print("\nSending request to LLM...")
        
        # Assuming OpenAI client for this example structure
        # Adapt if using Anthropic or Google
        if isinstance(QA_LLM_CONFIG, OpenAIConfig):
            response = qa_llm_client.chat.completions.create(
                model=QA_LLM_CONFIG.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": final_prompt}
                ]
            )
            answer = response.choices[0].message.content
        # Add elif for AnthropicConfig, GoogleConfig if desired, or abstract further
        else:
            # Simplified fallback or placeholder for other LLMs
            # In a real app, you'd implement the specific API calls here
            raise NotImplementedError(f"LLM client for {type(QA_LLM_CONFIG)} not fully implemented in this example.")

        return answer
    ```

4.  **Ask a Question!**

    Now, let's try it out.

    ```python
    my_question = "How does the authentication middleware handle expired JWTs?"
    # Or try: "What's the main purpose of the UserNotifications class's send_email method?"
    # Or: "Where is the database connection retry logic implemented in the db_utils module?"

    llm_answer = answer_question(my_question)
    print(f"\nLLM's Answer:\n{llm_answer}")
    ```

    ```text title="Example Output (will vary based on your repo & LLM)"
    Components initialized.
    Found existing index at ./my_code_qa_index_db/.

    Searching for files/symbols relevant to: 'How does the authentication middleware handle expired JWTs?'
    Found 3 relevant document summaries.
      1. Symbol: authenticate in src/auth/middleware.py (Type: function, Score: 0.8765)
      2. File: src/utils/jwt_helpers.py (Score: 0.7912)
      3. File: tests/auth/test_middleware.py (Score: 0.7500)

    Sending request to LLM...

    LLM's Answer:
    The `authenticate` function in `src/auth/middleware.py` checks for JWT expiration. If an `ExpiredSignatureError` is caught during token decoding (likely using a helper from `src/utils/jwt_helpers.py`), it returns a 401 Unauthorized response, typically with a JSON body like `{"error": "Token expired"}`.
    ```

</Steps>
```

File: /Users/darin/docs/kit/tutorials/docstring_search.mdx
```mdx
---
title: Build a Docstring Search Engine
---

In this tutorial you'll build a semantic search tool on top of `kit`
using **docstring-based indexing**. 

Why docstrings?  Summaries distill *intent* rather than syntax.  Embedding these
short natural-language strings lets the vector DB focus on meaning, giving you
relevant hits even when the literal code differs (e.g., `retry()` vs
`attempt_again()`).  It also keeps the index small (one embedding per file or
symbol instead of dozens of raw-code chunks).

---

## 1. Install dependencies

```bash
uv pip install kit sentence-transformers chromadb
```

## 2. Initialise a repo and summarizer

```python
import kit
from kit import Repository, DocstringIndexer, Summarizer, SummarySearcher
from sentence_transformers import SentenceTransformer

REPO_PATH = "/path/to/your/project"
repo = Repository(REPO_PATH)

summarizer = repo.get_summarizer()  # defaults to OpenAIConfig
```

## 3. Build the docstring index

```python
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_fn = lambda txt: embed_model.encode(txt).tolist()

indexer = DocstringIndexer(repo, summarizer, embed_fn)
indexer.build()          # writes REPO_PATH/.kit_cache/docstring_db
```

The first run will take time depending on repo size and LLM latency.
Summaries are cached inside the vector DB (and in a meta.json within the persist_dir), 
so subsequent runs are cheap if code hasn't changed.

## 4. Query the index

```python
searcher = indexer.get_searcher()

results = searcher.search("How is the retry back-off implemented?", top_k=3)
for hit in results:
    print(f"→ File: {hit.get('file_path', 'N/A')}\n  Summary: {hit.get('summary', 'N/A')}")
```

You now have a semantic code searcher, using powerful docstring summaries,
as easy as that.


```

File: /Users/darin/docs/kit/tutorials/integrating_supersonic.mdx
```mdx
---
title: Integrating with Supersonic
description: Using kit for code analysis and Supersonic for automated PR creation.
---

import { Aside } from '@astrojs/starlight/components';

`kit` excels at understanding and analyzing codebases, while [Supersonic](https://github.com/cased/supersonic) provides a high-level Python API specifically designed for programmatically creating GitHub Pull Requests. Combining them allows you to build powerful workflows that analyze code, generate changes, and automatically propose those changes via PRs.

<Aside type="note">
  **Use Case**
  Think of workflows like AI-powered code refactoring, automated dependency updates based on analysis, or generating documentation snippets from code and submitting them for review.
</Aside>

## The Workflow: Analyze with `kit`, Act with `Supersonic`

A typical integration pattern looks like this:

1.  **Analyze Code with `kit`**: Use `kit.Repository` methods like `extract_symbols`, `find_symbol_usages`, or `search_semantic` to understand the codebase or identify areas for modification.
2.  **Generate Changes**: Based on the analysis (potentially involving an LLM), generate the new code content or identify necessary file modifications.
3.  **Create PR with `Supersonic`**: Use `Supersonic`'s simple API (`create_pr_from_content`, `create_pr_from_file`, etc.) to package the generated changes into a new Pull Request on GitHub.

## Example: AI Refactoring Suggestion

Imagine an AI tool that uses `kit` to analyze a Python file, identifies a potential refactoring, generates the improved code, and then uses `Supersonic` to create a PR.

```python
import kit
from supersonic import Supersonic
import os

# Assume kit.Repository is initialized with a local path
LOCAL_REPO_PATH = "/path/to/your/local/repo/clone"
# repo_analyzer = kit.Repository(LOCAL_REPO_PATH)
# Note: kit analysis methods like extract_symbols would still be used here in a real scenario.

# Assume 'ai_generate_refactoring' is your function that uses an LLM
# potentially fed with context from kit (not shown here for brevity)
def ai_generate_refactoring(original_code: str) -> str:
    # ... your AI logic here ...
    improved_code = original_code.replace("old_function", "new_function") # Simplified example
    return improved_code

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER_SLASH_NAME = "your-org/your-repo" # For Supersonic PR creation
RELATIVE_FILE_PATH = "src/legacy_module.py" # Relative path within the repo
FULL_FILE_PATH = os.path.join(LOCAL_REPO_PATH, RELATIVE_FILE_PATH)
TARGET_BRANCH = "main" # Or dynamically determine

# --- Main Workflow ---

try:
    # 1. Get original content (assuming local repo)
    if not os.path.exists(FULL_FILE_PATH):
        print(f"Error: File not found at {FULL_FILE_PATH}")
        exit()

    with open(FULL_FILE_PATH, 'r') as f:
        original_content = f.read()

    # 2. Generate Changes (using AI or other logic)
    refactored_content = ai_generate_refactoring(original_content)

    if refactored_content != original_content:
        # 3. Create PR with Supersonic
        supersonic_client = Supersonic(GITHUB_TOKEN)
        pr_title = f"AI Refactor: Improve {RELATIVE_FILE_PATH}"
        pr_body = f"""
        AI analysis suggests refactoring in `{RELATIVE_FILE_PATH}`.

        This PR applies the suggested changes. Please review carefully.
        """

        pr_url = supersonic_client.create_pr_from_content(
            repo=REPO_OWNER_SLASH_NAME,
            content=refactored_content,
            upstream_path=RELATIVE_FILE_PATH, # Path within the target repo
            title=pr_title,
            description=pr_body,
            base_branch=TARGET_BRANCH,
            labels=["ai-refactor", "needs-review"],
            draft=True # Good practice for AI suggestions
        )
        print(f"Successfully created PR: {pr_url}")
    else:
        print("No changes generated.")

except Exception as e:
    print(f"An error occurred: {e}")

```

This example illustrates how `kit`'s analytical strengths can be combined with `Supersonic`'s action-oriented PR capabilities to build powerful code automation.

```

File: /Users/darin/docs/kit/tutorials/exploring-kit-interactively.mdx
```mdx
---
title: Exploring Kit Interactively with the Python Shell
description: A hands-on guide to trying out Kit's features directly in a Python interpreter.
---

import { Steps } from '@astrojs/starlight/components';

This guide walks you through interactively exploring the `kit` library's capabilities using a Python shell. This is a great way to quickly understand how different components work, test out methods, and see the structure of the data they return.

## Prerequisites

Before you begin, ensure you have:

1.  Cloned the `kit` repository.
2.  Set up your Python environment and installed `kit`'s dependencies. Ideally, you've installed `kit` in editable mode if you're also making changes:
    ```bash
    pip install -e .
    ```
3.  (Optional but recommended) Familiarized yourself with the [Core Concepts](/core-concepts/introduction) of `kit`.

## Getting Started: Your First Exploration

Let's dive in! We'll start by instantiating the `Repository` class and trying out some of its basic methods.

<Steps>

1.  **Launch your Python Interpreter**

    Open your terminal and start Python:
    ```bash
    python
    # or python3
    ```

2.  **Import `Repository` and Initialize**

    The `Repository` class is your main entry point for interacting with a codebase.

    ```python
    from kit.repository import Repository
    import os # We'll use this for path joining

    # Replace with the absolute path to your local clone of the 'kit' repository (or any other repo)
    # For example, if you are in the root of the 'kit' repo itself:
    repo_path = os.path.abspath(".") 
    # Or provide a full path directly:
    # repo_path = "/path/to/your/repository"

    repo = Repository(repo_path)
    print(repo) 
    # This should print something like: <Repository path=/path/to/your/repository, branch=main, files=XX>
    ```
    This confirms your `Repository` object is ready.

</Steps>

## Extracting Symbols from a File

One of the core features of `kit` is its ability to parse source code and extract meaningful symbols like classes, functions, and methods. The `repo.extract_symbols()` method is used for this. After recent updates, this method now provides the full source code for each symbol and the correct line numbers spanning the entire symbol definition.

<Steps>

1.  **Choose a File and Extract Symbols**

    Let's try extracting symbols from the `src/kit/repository.py` file itself.

    ```python
    # Assuming 'repo' is your Repository instance from the previous step
    # and 'os' is imported.

    file_to_test_relative = "src/kit/repository.py"
    full_file_path = os.path.join(repo.repo_path, file_to_test_relative)

    print(f"Extracting symbols from: {full_file_path}")
    symbols_in_repo_py = repo.extract_symbols(full_file_path)

    # You can use pprint for a more readable output of complex objects
    import pprint 
    # pprint.pprint(symbols_in_repo_py) # Uncomment to see all symbols
    ```

2.  **Inspect a Specific Symbol**

    Let's look at the first symbol extracted, which should be the `Repository` class itself.

    ```python
    if symbols_in_repo_py:
        repository_class_symbol = None
        for sym in symbols_in_repo_py:
            if sym.get('name') == 'Repository' and sym.get('type') == 'class':
                repository_class_symbol = sym
                break
        
        if repository_class_symbol:
            print("\n--- Details for 'Repository' class symbol ---")
            print(f"Name: {repository_class_symbol.get('name')}")
            print(f"Type: {repository_class_symbol.get('type')}")
            print(f"Start Line: {repository_class_symbol.get('start_line')}")
            print(f"End Line: {repository_class_symbol.get('end_line')}")
            print(f"File: {repository_class_symbol.get('file')}") # Though we know the file, it's good to see it in the output
            print("\nCode (first ~300 characters):")
            print(repository_class_symbol.get('code', '')[:300] + "...")
            print(f"\n(Full code length: {len(repository_class_symbol.get('code', ''))} characters)")
            print("------")
        else:
            print("Could not find the 'Repository' class symbol.")
    else:
        print(f"No symbols extracted from {file_to_test_relative}")
    ```

    You should see that:
    *   The `code` field contains the *entire* source code of the `Repository` class.
    *   `start_line` and `end_line` accurately reflect the beginning and end of the class definition.
    *   This is a significant improvement, providing much richer data for analysis or use in LLM prompts.

</Steps>

## Listing All Files in the Repository

To get an overview of all files and directories that `kit` recognizes within your repository, you can use the `repo.get_file_tree()` method. This is helpful for understanding the scope of what `kit` will operate on.

<Steps>

1.  **Call `get_file_tree()`**

    ```python
    # Assuming 'repo' is your Repository instance

    print("\n--- Getting File Tree ---")
    file_tree = repo.get_file_tree()

    if file_tree:
        print(f"Found {len(file_tree)} files/items in the repository.")
        print("\nFirst 5 items in the file tree:")
        for i, item in enumerate(file_tree[:5]): # Print the first 5 items
            print(f"{i+1}. {item}")
        print("------")
        
        # Example of what one item might look like:
        # {'path': 'src/kit/repository.py', 'is_dir': False, 'name': 'repository.py', 'size': 14261}
    else:
        print("File tree is empty or could not be retrieved.")
    ```

2.  **Understanding the Output**

    The `get_file_tree()` method returns a list of dictionaries. Each dictionary represents a file or directory and typically includes:
    *   `'path'`: The relative path from the repository root.
    *   `'is_dir'`: `True` if it's a directory, `False` if it's a file.
    *   `'name'`: The base name of the file or directory.
    *   `'size'`: The size in bytes (often 0 for directories in this view).

    This method respects rules defined in `.gitignore` (by default) and gives you a snapshot of the files `kit` is aware of.

</Steps>

## Searching for Text in Files

`kit` allows you to perform text-based searches across your repository, similar to using `grep`. This is handled by the `repo.search_text()` method.

<Steps>

1.  **Perform a Search (Default: All Files)**

    Let's search for the term "app". By default, `search_text` now looks in all files (`*`).

    ```python
    # Assuming 'repo' is your Repository instance

    print("\n--- Searching for Text ---")
    query_text = "app"
    # The default file_pattern is now "*", so it searches all files
    search_results_all = repo.search_text(query=query_text)

    if search_results_all:
        print(f"Found {len(search_results_all)} occurrences of '{query_text}' in all files.")
        print("\nFirst 3 search results (all files):")
        for i, result in enumerate(search_results_all[:3]):
            print(f"\nResult {i+1}:")
            print(f"  File: {result.get('file')}")
            print(f"  Line Number (0-indexed): {result.get('line_number')}") 
            print(f"  Line Content: {result.get('line', '').strip()}")
    else:
        print(f"No occurrences of '{query_text}' found in any files.")
    print("------")
    ```

2.  **Search in Specific File Types**

    You can still specify a `file_pattern` to search in specific file types. For example, to search for "Repository" only in Python (`*.py`) files:

    ```python
    query_repo = "Repository"
    pattern_py = "*.py"
    print(f"\nSearching for '{query_repo}' in '{pattern_py}' files...")
    repo_py_results = repo.search_text(query=query_repo, file_pattern=pattern_py)

    if repo_py_results:
        print(f"Found {len(repo_py_results)} occurrences of '{query_repo}' in Python files.")
        print("First result (Python files):")
        first_py_result = repo_py_results[0]
        print(f"  File: {first_py_result.get('file')}")
        print(f"  Line Number (0-indexed): {first_py_result.get('line_number')}")
        print(f"  Line Content: {first_py_result.get('line', '').strip()}")
    else:
        print(f"No occurrences of '{query_repo}' found in '{pattern_py}' files.")
    print("------")
    ```

3.  **Understanding the Output**

    `search_text()` returns a list of dictionaries, each representing a match. Key fields include:
    *   `'file'`: The path to the file where the match was found.
    *   `'line_number'`: The (often 0-indexed) line number of the match.
    *   `'line'`: The full content of the line containing the match.
    *   `'context_before'` and `'context_after'`: Lists for lines before/after the match (may be empty depending on search configuration).

    Keep in mind this is a literal text search and is case-sensitive by default. It will find the query string as a substring anywhere it appears (e.g., "app" within "mapper" or "happy").

</Steps>

## Workflow: Get First File's Content

A common task is to list files, select one, and then retrieve its contents. Here's a simple workflow to get the content of the first file listed by `get_file_tree()`.

<Steps>

1.  **Get File Tree, Pick First File, and Get Content**

    This script finds the first item in the `file_tree` that is a file (not a directory) and prints a snippet of its content.

    ```python
    # Assuming 'repo' is your Repository instance

    print("\n--- Workflow: Get First *File's* Content ---")

    # 1. List all items
    file_tree = repo.get_file_tree()

    first_file_path = None
    if file_tree:
        # 2. Find the path of the first actual file in the tree
        for item in file_tree:
            if not item.get('is_dir', False): # Make sure it's a file
                first_file_path = item['path']
                break # Stop once we've found the first file

    if not first_file_path:
        print("No actual files (non-directories) found in the repository.")
    else:
        print(f"\nPicking the first *file* found in the tree: {first_file_path}")

        # 3. Get its content
        print(f"Attempting to read content from: {first_file_path}")
        try:
            content = repo.get_file_content(first_file_path)
            print(f"\n--- Content of {first_file_path} (first 300 chars) ---")
            print(content[:300] + "..." if len(content) > 300 else content)
            print(f"------ End of {first_file_path} snippet ------")
        except FileNotFoundError:
            print(f"Error: File not found at '{first_file_path}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    print("------")
    ```

2.  **Example Output**

    If the first file in your repository is `LICENSE`, the output might look like:

    ```text
    --- Workflow: Get First *File's* Content ---

    Picking the first *file* found in the tree: LICENSE
    Attempting to read content from: LICENSE

    --- Content of LICENSE (first 300 chars) ---
    MIT License

    Copyright (c) 2024 Cased

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, dis...
    ------ End of LICENSE snippet ------
    ------
    ```

    This demonstrates successfully using `get_file_tree()` to discover a file and `get_file_content()` to read it.

</Steps>

### Chunking File Content by Lines (`repo.chunk_file_by_lines()`)

The `Repository` class provides a method to break down a file's content into smaller string chunks based on a target maximum number of lines. This is useful for preprocessing text for Large Language Models (LLMs) or other tools that have input size limits.

The method signature is: `repo.chunk_file_by_lines(file_path: str, max_lines: int = 50) -> List[str]`

-   `file_path`: The relative path to the file within the repository.
-   `max_lines`: The desired maximum number of lines for each chunk. The actual number of lines in a chunk might vary slightly as the method attempts to find reasonable break points.
-   It returns a list of strings, where each string is a content chunk.

**Example 1: Chunking a small file (e.g., `LICENSE`)**

If the file is smaller than `max_lines`, it will be returned as a single chunk.

```python
license_path = "LICENSE"
license_chunks = repo.chunk_file_by_lines(license_path)

print(f"Number of chunks for {license_path}: {len(license_chunks)}")
if license_chunks:
    print(f"Content of the first chunk (first 50 chars):\n---\n{license_chunks[0][:50]}...\n---")
```

**Expected Output (for `LICENSE`):**

```text
Number of chunks for LICENSE: 1
Content of the first chunk (first 50 chars):
---
MIT License

Copyright (c) 2024 Cased

Permiss...
---
```

**Example 2: Chunking a larger file (e.g., `src/kit/repository.py`)**

For larger files, the content will be split into multiple string chunks.

```python
repo_py_path = "src/kit/repository.py"
repo_py_chunks = repo.chunk_file_by_lines(repo_py_path, max_lines=50)

print(f"\nNumber of chunks for {repo_py_path} (with max_lines=50): {len(repo_py_chunks)}")

for i, chunk_content in enumerate(repo_py_chunks[:2]):
    print(f"\n--- Chunk {i+1} for {repo_py_path} ---")
    print(f"  Approx. line count: {len(chunk_content.splitlines())}")
    print(f"  Content (first 100 chars):\n  \"\"\"\n{chunk_content[:100]}...\n  \"\"\"")
```

**Expected Output (for `src/kit/repository.py`, showing 2 of 7 chunks):**

```text
Number of chunks for src/kit/repository.py (with max_lines=50): 7

--- Chunk 1 for src/kit/repository.py ---
  Approx. line count: 48
  Content (first 100 chars):
  """
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Unio...
  """

--- Chunk 2 for src/kit/repository.py ---
  Approx. line count: 20 
  Content (first 100 chars):
  """
                    # If not on a branch (detached HEAD), get commit SHA
                    sha_cmd = ["git", "rev...
  """
```
*(Note: Actual line counts per chunk may vary slightly based on how the chunker splits the content. The second chunk from your output had fewer lines than the first.)*

### Chunking File Content by Symbols (`repo.chunk_file_by_symbols()`)

A more semantically aware way to chunk files is by symbols. This method uses `kit`'s understanding of code structure to break the file into chunks that correspond to whole symbols like functions, classes, or methods. Each chunk represents a meaningful structural unit of the code.

The method signature is: `repo.chunk_file_by_symbols(file_path: str) -> List[Dict[str, Any]]`

-   `file_path`: The relative path to the file within the repository.
-   It returns a list of dictionaries. Each dictionary represents one symbol-chunk and contains details like the symbol's `name`, `type`, `code` content, and `start_line`/`end_line` numbers.

**Example: Chunking `src/kit/tree_sitter_symbol_extractor.py` by symbols**

```python
extractor_path = "src/kit/tree_sitter_symbol_extractor.py"
symbol_chunks = repo.chunk_file_by_symbols(file_path=extractor_path)

print(f"Successfully chunked '{extractor_path}' into {len(symbol_chunks)} symbol-based chunks.")

for i, chunk_dict in enumerate(symbol_chunks[:2]): # Show first 2 symbol chunks
    print(f"\n--- Symbol Chunk {i+1} ---")
    symbol_name = chunk_dict.get('name', 'N/A')
    symbol_type = chunk_dict.get('type', 'N/A')
    start_line = chunk_dict.get('start_line', 'N/A')
    end_line = chunk_dict.get('end_line', 'N/A')
    code_content = chunk_dict.get('code', '')
    
    print(f"  Symbol Name: {symbol_name}")
    print(f"  Symbol Type: {symbol_type}")
    print(f"  Start Line (0-indexed): {start_line}")
    print(f"  End Line (0-indexed): {end_line}")
    print(f"  Line Count of code: {len(code_content.splitlines())}")
    print(f"  Content (first 150 chars of code):\n  \"\"\"\n{code_content[:150]}...\n  \"\"\"")
```

**Expected Output (for `src/kit/tree_sitter_symbol_extractor.py`, showing 2 of 4 chunks):**

```text
Successfully chunked 'src/kit/tree_sitter_symbol_extractor.py' into 4 symbol-based chunks.

--- Symbol Chunk 1 ---
  Symbol Name: TreeSitterSymbolExtractor
  Symbol Type: class
  Start Line (0-indexed): 28
  End Line (0-indexed): 197
  Line Count of code: 170
  Content (first 150 chars of code):
  """
class TreeSitterSymbolExtractor:
    """
    Multi-language symbol extractor using tree-sitter queries (tags.scm).
    Register new languages by addin...
  """

--- Symbol Chunk 2 ---
  Symbol Name: get_parser
  Symbol Type: method
  Start Line (0-indexed): 38
  End Line (0-indexed): 45
  Line Count of code: 8
  Content (first 150 chars of code):
  """
def get_parser(cls, ext: str) -> Optional[Any]:
        if ext not in LANGUAGES:
            return None
        if ext not in cls._parsers:
         ...
  """
```

This provides a more structured way to access and process individual components of a code file.

We'll add more examples here as we try them out.

*(This document will be updated as we explore more features.)*

```

File: /Users/darin/docs/kit/tutorials/recipes.mdx
```mdx
---
title: Practical Recipes
---

:::note
These snippets are *copy-paste-ready* solutions for common developer-productivity tasks with **kit**. Adapt them to scripts, CI jobs, or IDE plugins.
:::

## 1. Rename every function `old_name` → `new_name`

```python
from pathlib import Path
from kit import Repository

repo = Repository("/path/to/project")

# Gather definitions & references (quick heuristic)
usages = repo.find_symbol_usages("old_name", symbol_type="function")

edits: dict[str, str] = {}
for u in usages:
    path, line = u["file"], u.get("line")
    if line is None:
        continue
    lines = repo.get_file_content(path).splitlines()
    lines[line] = lines[line].replace("old_name", "new_name")
    edits[path] = "\n".join(lines) + "\n"

# Apply edits – prompt the user first!
for rel_path, new_src in edits.items():
    Path(repo.repo_path, rel_path).write_text(new_src)

repo.mapper.scan_repo()  # refresh symbols if you'll run more queries
```

---

## 2. Summarize a Git diff for an LLM PR review

```python
from kit import Repository
# Assuming OpenAI for this example, and API key is set in environment
from kit.summaries import OpenAIConfig 

repo = Repository(".")
assembler = repo.get_context_assembler()
# diff_text would be a string containing the output of `git diff`
# Example: 
# diff_text = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True).stdout

# Ensure diff_text is populated before this step in a real script
diff_text = """diff --git a/file.py b/file.py
index 0000000..1111111 100644
--- a/file.py
+++ b/file.py
@@ -1,1 +1,1 @@
-old line
+new line
""" # Placeholder diff_text

assembler.add_diff(diff_text)
context_blob = assembler.format_context()

# Get the summarizer and its underlying LLM client to summarize arbitrary text
# This example assumes you want to use the default OpenAI configuration for the summarizer.
# If you have a specific config (OpenAI, Anthropic, Google), pass it to get_summarizer.
summarizer_instance = repo.get_summarizer() # Uses default OpenAIConfig
llm_client = summarizer_instance._get_llm_client() # Access the configured client

summary = "Could not generate summary."
if hasattr(llm_client, 'chat') and hasattr(llm_client.chat, 'completions'): # OpenAI-like client
    try:
        response = llm_client.chat.completions.create(
            model=summarizer_instance.config.model if summarizer_instance.config else "gpt-4o", # Get model from config
            messages=[
                {"role": "system", "content": "You are an expert software engineer. Please summarize the following code changes and context."},
                {"role": "user", "content": context_blob}
            ],
            temperature=0.2,
            max_tokens=500 # Adjust as needed
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        summary = f"Error generating summary: {e}"
elif hasattr(llm_client, 'messages') and hasattr(llm_client.messages, 'create'): # Anthropic-like client
    try:
        response = llm_client.messages.create(
            model=summarizer_instance.config.model if summarizer_instance.config else "claude-3-opus-20240229",
            system="You are an expert software engineer. Please summarize the following code changes and context.",
            messages=[
                {"role": "user", "content": context_blob}
            ],
            max_tokens=500,
            temperature=0.2,
        )
        summary = response.content[0].text.strip()
    except Exception as e:
        summary = f"Error generating summary: {e}"
# Add similar elif for Google GenAI client if needed, or abstract this LLM call further

print(summary)
```

---

## 3. Semantic search for authentication code

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embed = lambda text: model.encode([text])[0].tolist()

repo = Repository(".")
vs = repo.get_vector_searcher(embed_fn=embed)
vs.build_index()

hits = repo.search_semantic("How is user authentication handled?", embed_fn=embed)
for h in hits:
    print(h["file"], h.get("name"))
```

---

## 4. Export full repo index to JSON (file tree + symbols)

```python
repo = Repository("/path/to/project")
repo.write_index("repo_index.json")
```

---

## 5. Find All Callers of a Specific Function (Cross-File)

This recipe helps you understand where a particular function is being used throughout your entire codebase, which is crucial for impact analysis or refactoring.

```python
from kit import Repository

# Initialize the repository
repo = Repository("/path/to/your_project")

# Specify the function name and its type
function_name_to_trace = "my_target_function"

# Find all usages (definitions, calls, imports)
usages = repo.find_symbol_usages(function_name_to_trace, symbol_type="function")

print(f"Usages of function '{function_name_to_trace}':")
for usage in usages:
    file_path = usage.get("file")
    line_number = usage.get("line") # Assuming 'line' is the start line of the usage/symbol
    context_snippet = usage.get("context", "No context available")
    usage_type = usage.get("type", "unknown") # e.g., 'function' for definition, 'call' for a call site

    # We are interested in where it's CALLED, so we might filter out the definition itself if needed,
    # or differentiate based on the 'type' or 'context'.
    # For this example, we'll print all usages.
    if line_number is not None:
        print(f"- Found in: {file_path}:L{line_number + 1}") # (line is 0-indexed, display as 1-indexed)
    else:
        print(f"- Found in: {file_path}")
    print(f"    Type: {usage_type}")
    print(f"    Context: {context_snippet.strip()}\n")

# Example: Filtering for actual call sites (heuristic based on context or type if available)
# print(f"\nCall sites for function '{function_name_to_trace}':")
# for usage in usages:
#     # This condition might need refinement based on what 'find_symbol_usages' returns for 'type' of a call
#     if usage.get("type") != "function" and function_name_to_trace + "(" in usage.get("context", ""):
#         file_path = usage.get("file")
#         line_number = usage.get("line")
#         print(f"- Call in: {file_path}:L{line_number + 1 if line_number is not None else 'N/A'}")

```

---

## 6. Identify Potentially Unused Functions (Heuristic)

This recipe provides a heuristic to find functions that *might* be unused within the analyzed codebase. This can be a starting point for identifying dead code. Note that this is a heuristic because it might not catch dynamically called functions, functions part of a public API but not used internally, or functions used only in parts of the codebase not analyzed (e.g., separate test suites).

```python
from kit import Repository

repo = Repository("/path/to/your_project")

# Get all symbols from the repository index
# The structure of repo.index() might vary; assuming it's a dict like {'symbols': {'file_path': [symbol_dicts]}}
# or a direct way to get all function definitions.
# For this example, let's assume we can iterate through all symbols and filter functions.

# A more robust way might be to iterate files, then symbols within files from repo.index()
# index = repo.index()
# all_symbols_by_file = index.get("symbols", {})

print("Potentially unused functions:")

# First, get a list of all function definitions
defined_functions = []
repo_index = repo.index() # Assuming this fetches file tree and symbols
symbols_map = repo_index.get("symbols", {})

for file_path, symbols_in_file in symbols_map.items():
    for symbol_info in symbols_in_file:
        if symbol_info.get("type") == "function":
            defined_functions.append({
                "name": symbol_info.get("name"),
                "file": file_path,
                "line": symbol_info.get("line_start", 0) # or 'line'
            })

for func_def in defined_functions:
    function_name = func_def["name"]
    definition_file = func_def["file"]
    definition_line = func_def["line"]

    if not function_name: # Skip if name is missing
        continue

    usages = repo.find_symbol_usages(function_name, symbol_type="function")

    # Filter out the definition itself from the usages to count actual calls/references
    # This heuristic assumes a usage is NOT the definition if its file and line differ,
    # or if the usage 'type' (if available and detailed) indicates a call.
    # A simpler heuristic: if only 1 usage, it's likely just the definition.
    
    actual_references = []
    for u in usages:
        # Check if the usage is different from the definition site
        if not (u.get("file") == definition_file and u.get("line") == definition_line):
            actual_references.append(u)
    
    # If a function has no other references apart from its own definition site (or very few)
    # It's a candidate for being unused. The threshold (e.g., 0 or 1) can be adjusted.
    if len(actual_references) == 0:
        print(f"- Function '{function_name}' defined in {definition_file}:L{definition_line + 1} has no apparent internal usages.")

:::caution[Limitations of this heuristic:]
**Limitations of this heuristic:**

*   **Dynamic Calls:** Functions called dynamically (e.g., through reflection, or if the function name is constructed from a string at runtime) won't be detected as used.
*   **Public APIs:** Functions intended for external use (e.g., library functions) will appear unused if the analysis is limited to the library's own codebase.
*   **Test Code:** If your test suite is separate and not part of the `Repository` path being analyzed, functions used only by tests might be flagged.
*   **Object Methods:** The `symbol_type="function"` might need adjustment or further logic if you are also looking for unused *methods* within classes, as their usage context is different.
:::

```

File: /Users/darin/docs/kit/index.mdx
```mdx
---
title: 🛠️ kit documentation
template: doc
tableOfContents: false
bodyClass: kit-homepage
---

import Card from "../../components/Card.astro";
import CardGroup from "../../components/CardGroup.astro";

<div class="hero-container">
  <div class="hero-image">
    <img src="/kit.png" alt="Kit Toolkit Logo" />
  </div>
  <div class="hero-text">
    Welcome to **kit** – the Python toolkit from [Cased](https://cased.com) for building LLM-powered developer tools and workflows.

    kit shines for getting **precise, accurate, and relevant context** to 
    LLMs. Use kit to build code reviewers, code generators and graphs, even full-fledged coding assistants: all enriched with the right code context. 
    
    MIT-licensed on [GitHub](https://github.com/cased/kit).
  </div>
</div>

<hr />

{/* Features Section - Full Width Items */}

<div style="display: flex; flex-direction: column; gap: 1rem; margin-top: 1.5rem; margin-bottom: 2rem;">
  <div style="padding: 1.25rem; border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem;">
    <h4 style="margin-top: 0; font-size: 1.1rem;">Map any codebase</h4>
    <p style="font-size: 0.95rem; color: var(--sl-color-gray-2); margin-bottom: 0;">
      Get a structured view with file trees, language-aware symbol extraction
      (powered by tree-sitter), and dependency insights.
    </p>
  </div>
  <div style="padding: 1.25rem; border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem;">
    <h4 style="margin-top: 0; font-size: 1.1rem;">
      Support for multiple search methods
    </h4>
    <p style="font-size: 0.95rem; color: var(--sl-color-gray-2); margin-bottom: 0;">
      Mix and match to optimize for speed, accuracy, and use case. Combine fast
      text search with semantic vector search to find relevant code snippets
      instantly.
    </p>
  </div>
  <div style="padding: 1.25rem; border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem;">
    <h4 style="margin-top: 0; font-size: 1.1rem;">
      Fine-grained docstring context
    </h4>
    <p style="font-size: 0.95rem; color: var(--sl-color-gray-2); margin-bottom: 0;">
      Use generated docstrings to find code snippets, answer questions, and
      improve code generation based on summarized content.
    </p>
  </div>
  <div style="padding: 1.25rem; border: 1px solid var(--sl-color-gray-5); border-radius: 0.5rem;">
    <h4 style="margin-top: 0; font-size: 1.1rem;">Build AI Workflows</h4>
    <p style="font-size: 0.95rem; color: var(--sl-color-gray-2); margin-bottom: 0;">
      Leverage ready-made utilities for code chunking, context retrieval, and
      interacting with LLMs.
    </p>
  </div>
</div>

## Explore the docs

<CardGroup cols={2}>
  <Card title="Overview" href="/introduction/overview">
    What Kit is, why it exists, and how to install it.
  </Card>
  <Card title="Core Concepts" href="/core-concepts/repository-api">
    Deep-dive into the Repository API, symbol extraction, vector search, and
    architecture.
  </Card>
  <Card title="Tutorials" href="/tutorials/ai_pr_reviewer">
    Step-by-step tutorials to build real-world tools with Kit.
  </Card>
  <Card title="API docs" href="/api/repository">
    Detailed API documentation for the primary classes.
  </Card>
</CardGroup>

```

File: /Users/darin/docs/kit/README.mdx
```mdx
---
title: Documentation
description: Documentation for kit.
---

This uses [Starlight](https://starlight.astro.build) to build the documentation.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `pnpm install`             | Installs dependencies                            |
| `pnpm dev`             | Starts local dev server at `localhost:4321`      |
| `pnpm build`           | Build your production site to `./dist/`          |
| `pnpm preview`         | Preview your build locally, before deploying     |
| `pnpm astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `pnpm astro -- --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Check out [Starlight’s docs](https://starlight.astro.build/), read [the Astro documentation](https://docs.astro.build), or jump into the [Astro Discord server](https://astro.build/chat).

```

File: /Users/darin/docs/kit/recipes.mdx
```mdx
---
title: Practical Recipes
---

:::note
These snippets are *copy-paste-ready* solutions for common developer-productivity tasks with **kit**. Adapt them to scripts, CI jobs, or IDE plugins.
:::

## 1. Rename every function `old_name` → `new_name`

```python
from pathlib import Path
from kit import Repository

repo = Repository("/path/to/project")

# Gather definitions & references (quick heuristic)
usages = repo.find_symbol_usages("old_name", symbol_type="function")

edits: dict[str, str] = {}
for u in usages:
    path, line = u["file"], u.get("line")
    if line is None:
        continue
    lines = repo.get_file_content(path).splitlines()
    lines[line] = lines[line].replace("old_name", "new_name")
    edits[path] = "\n".join(lines) + "\n"

# Apply edits – prompt the user first!
for rel_path, new_src in edits.items():
    Path(repo.repo_path, rel_path).write_text(new_src)

repo.mapper.scan_repo()  # refresh symbols if you’ll run more queries
```

---

## 2. Summarize a Git diff for an LLM PR review

```python
from kit import Repository
repo = Repository(".")
assembler = repo.get_context_assembler()
assembler.add_diff(diff_text)  # diff_text from `git diff`
summary = repo.get_summarizer().summarize(assembler.format_context())
print(summary)
```

---

## 3. Semantic search for authentication code

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embed = lambda text: model.encode([text])[0].tolist()

repo = Repository(".")
vs = repo.get_vector_searcher(embed_fn=embed)
vs.build_index()

hits = repo.search_semantic("How is user authentication handled?", embed_fn=embed)
for h in hits:
    print(h["file"], h.get("name"))
```

---

## 4. Export full repo index to JSON (file tree + symbols)

```python
repo = Repository("/path/to/project")
repo.write_index("repo_index.json")
```

---

## 5. Find All Callers of a Specific Function (Cross-File)

This recipe helps you understand where a particular function is being used throughout your entire codebase, which is crucial for impact analysis or refactoring.

```python
from kit import Repository

# Initialize the repository
repo = Repository("/path/to/your_project")

# Specify the function name and its type
function_name_to_trace = "my_target_function"

# Find all usages (definitions, calls, imports)
usages = repo.find_symbol_usages(function_name_to_trace, symbol_type="function")

print(f"Usages of function '{function_name_to_trace}':")
for usage in usages:
    file_path = usage.get("file")
    line_number = usage.get("line") # Assuming 'line' is the start line of the usage/symbol
    context_snippet = usage.get("context", "No context available")
    usage_type = usage.get("type", "unknown") # e.g., 'function' for definition, 'call' for a call site

    # We are interested in where it's CALLED, so we might filter out the definition itself if needed,
    # or differentiate based on the 'type' or 'context'.
    # For this example, we'll print all usages.
    if line_number is not None:
        print(f"- Found in: {file_path}:L{line_number + 1}") # (line is 0-indexed, display as 1-indexed)
    else:
        print(f"- Found in: {file_path}")
    print(f"    Type: {usage_type}")
    print(f"    Context: {context_snippet.strip()}\n")

# Example: Filtering for actual call sites (heuristic based on context or type if available)
# print(f"\nCall sites for function '{function_name_to_trace}':")
# for usage in usages:
#     # This condition might need refinement based on what 'find_symbol_usages' returns for 'type' of a call
#     if usage.get("type") != "function" and function_name_to_trace + "(" in usage.get("context", ""):
#         file_path = usage.get("file")
#         line_number = usage.get("line")
#         print(f"- Call in: {file_path}:L{line_number + 1 if line_number is not None else 'N/A'}")

```

---

## 6. Identify Potentially Unused Functions (Heuristic)

This recipe provides a heuristic to find functions that *might* be unused within the analyzed codebase. This can be a starting point for identifying dead code. Note that this is a heuristic because it might not catch dynamically called functions, functions part of a public API but not used internally, or functions used only in parts of the codebase not analyzed (e.g., separate test suites).

```python
from kit import Repository

repo = Repository("/path/to/your_project")

# Get all symbols from the repository index
# The structure of repo.index() might vary; assuming it's a dict like {'symbols': {'file_path': [symbol_dicts]}}
# or a direct way to get all function definitions.
# For this example, let's assume we can iterate through all symbols and filter functions.

# A more robust way might be to iterate files, then symbols within files from repo.index()
# index = repo.index()
# all_symbols_by_file = index.get("symbols", {})

print("Potentially unused functions:")

# First, get a list of all function definitions
defined_functions = []
repo_index = repo.index() # Assuming this fetches file tree and symbols
symbols_map = repo_index.get("symbols", {})

for file_path, symbols_in_file in symbols_map.items():
    for symbol_info in symbols_in_file:
        if symbol_info.get("type") == "function":
            defined_functions.append({
                "name": symbol_info.get("name"),
                "file": file_path,
                "line": symbol_info.get("line_start", 0) # or 'line'
            })

for func_def in defined_functions:
    function_name = func_def["name"]
    definition_file = func_def["file"]
    definition_line = func_def["line"]

    if not function_name: # Skip if name is missing
        continue

    usages = repo.find_symbol_usages(function_name, symbol_type="function")

    # Filter out the definition itself from the usages to count actual calls/references
    # This heuristic assumes a usage is NOT the definition if its file and line differ,
    # or if the usage 'type' (if available and detailed) indicates a call.
    # A simpler heuristic: if only 1 usage, it's likely just the definition.
    
    actual_references = []
    for u in usages:
        # Check if the usage is different from the definition site
        if not (u.get("file") == definition_file and u.get("line") == definition_line):
            actual_references.append(u)
    
    # If a function has no other references apart from its own definition site (or very few)
    # It's a candidate for being unused. The threshold (e.g., 0 or 1) can be adjusted.
    if len(actual_references) == 0:
        print(f"- Function '{function_name}' defined in {definition_file}:L{definition_line + 1} has no apparent internal usages.")

:::caution[Limitations of this heuristic:]
**Limitations of this heuristic:**

*   **Dynamic Calls:** Functions called dynamically (e.g., through reflection, or if the function name is constructed from a string at runtime) won't be detected as used.
*   **Public APIs:** Functions intended for external use (e.g., library functions) will appear unused if the analysis is limited to the library's own codebase.
*   **Test Code:** If your test suite is separate and not part of the `Repository` path being analyzed, functions used only by tests might be flagged.
*   **Object Methods:** The `symbol_type="function"` might need adjustment or further logic if you are also looking for unused *methods* within classes, as their usage context is different.
:::

```
</file_contents>



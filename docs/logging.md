# Logging Guide

This project uses **logkit** for all telemetry. Every log line is structured JSON and automatically correlated by `trace_id` and `span_id`.

## Getting Started

1. Import the helpers:

   ```python
   from logkit import log, new_context, capture
   ```

2. At each entry point call `new_context()` once to start a new trace. Provide any useful identifiers as keyword arguments. Example for the CLI:

   ```python
   def main():
       new_context(cmd="cli")
       with capture(cli="run"):
           ...
   ```

3. Wrap the main work in `capture()` either as a decorator or context manager. A single END record with duration and success or error status is emitted.

4. Use `log.info()` (or `.debug()` / `.error()`) as you normally would. Context set via `new_context()` or `capture()` is automatically added to every log line.

## Environment Configuration

- `LOG_PROFILE`: `dev` (pretty console + DEBUG) or `prod` (JSON + INFO). Defaults to `dev`.
- `LOG_LEVEL`: Override the minimum log level.
- `LOG_SAMPLE`: Fraction of DEBUG/INFO logs kept in `prod` profile.
- `LOG_FILE`: Path to the JSONL log file. Defaults to `run.log`. Set empty to disable.
- `LOG_ROTATE_MB`: Size in MiB before log files rotate. Five backups are kept.

## Debugging with Logs

1. Run a command with production formatting and capture the output:

   ```bash
   LOG_PROFILE=prod python -m ai_pr_review owner repo 123 > run.jsonl
   ```

2. Use `jq` or `rg` to filter by `trace_id` or search for errors:

   ```bash
   jq -c 'select(.status=="error")' run.jsonl
   rg "\"trace_id\": \"<id>\"" run.jsonl
   ```

3. Each log entry records the duration in milliseconds. Compare spans to locate slow steps.

## When to Log

- Log significant steps in `review.py` or other workflows so that failures can be traced after the fact.
- Prefer `log.info()` for normal progress messages and `log.debug()` for verbose details.
- Errors should be logged using `log.exception()` within a `capture()` block. The exception info is attached automatically.

## Type Checking

A stub file `logkit.pyi` ships with this repo so `log`, `new_context`, and `capture` have proper types. Simply import them—no cast is required in your modules.

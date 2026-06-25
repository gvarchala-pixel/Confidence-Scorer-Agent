# Basic Confidence Scorer

A simple terminal-based confidence scorer app. It is meant as a small learning project to show how a local Python CLI can call an LLM service, gather evidence, and estimate confidence for an assertion.

## What this does

- Runs from the command line
- Uses a local LLM backend for text understanding
- Produces a basic confidence-style score for a query
- Keeps the setup intentionally small and easy to follow

## Tech stack

- Python 3.10+ for the application
- `uv` as a lightweight package manager and virtual environment helper
- `Ollama` for a local LLM endpoint (the service that runs the language model)
- Optional web search support via DuckDuckGo or Tavily

## Requirements

- Python 3.10 or newer
- `uv` installed (`pip install uv` or follow https://docs.astral.sh/uv/)
- `Ollama` installed and running locally
- A pulled model for Ollama, for example:

```bash
ollama pull llama3.2
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and set these values:

- `OLLAMA_BASE_URL` – the local URL for your Ollama server, for example `http://127.0.0.1:11434`
- `LLM_MODEL` – the model name you want to use with Ollama
- `WEB_SEARCH_PROVIDER` – optional, defaults to `duckduckgo`
- `TAVILY_API_KEY` – optional, only needed if using `tavily`

> `OLLAMA_BASE_URL` is the address where the local model server is reachable.
> `TAVILY_API_KEY` is only required when using Tavily search; DuckDuckGo does not need a key.

## Setup

```bash
uv sync
source .venv/bin/activate
```

If `uv sync` creates a `.venv`, the `source` command activates the virtual environment.

## Running locally

Use the provided CLI entrypoint. For example:

```bash
python -m aletheia.cli "Is regular exercise linked to better memory?"
```

If the repository installs a script entrypoint, you can also run:

```bash
uv run aletheia "Is regular exercise linked to better memory?"
```

## Optional search provider

The project can use DuckDuckGo without extra setup.

To enable Tavily search instead:

1. Set `WEB_SEARCH_PROVIDER=tavily` in `.env`
2. Add `TAVILY_API_KEY=<your-key>` to `.env`

## Tests

Run the test suite with:

```bash
uv run pytest
```

## Notes

This is a minimal, experimental repository for exploring confidence scoring with a local LLM service. It is not a production system.

## License

MIT

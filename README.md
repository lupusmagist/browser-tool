# Browser Tool API

A FastAPI-based web service that provides browser automation and web search capabilities using Playwright and SearXNG.

## Features

- **Web Search**: Search the web using your SearXNG instance
- **Web Navigation**: Navigate to URLs with optional element waiting
- **Content Extraction**: Extract clean text content from web pages
- **Text Summarization**: Summarize text using a local LLM (Llama)
- **Web Crawling**: Crawl websites with depth control (placeholder)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Configure environment variables in `.env`:
```
LLM="/path/to/your/model.gguf"
SEARXNG_URL="http://192.168.77.8:8888"
```

3. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Web Search
Search the web using SearXNG.

```bash
curl -X POST "http://localhost:8000/web_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python programming tutorials", "max_results": 5}'
```

**Request Body:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Maximum number of results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "snippet": "Result description..."
    }
  ]
}
```

### Navigate
Navigate to a URL with optional element waiting.

```bash
curl -X POST "http://localhost:8000/navigate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "wait_for_element": ".content", "wait_time": 10}'
```

**Request Body:**
- `url` (string, required): URL to navigate to
- `wait_for_element` (string, optional): CSS selector to wait for
- `wait_time` (integer, optional): Timeout in seconds (default: 10)

### Extract Content
Extract clean text content from a web page.

```bash
curl -X POST "http://localhost:8000/extract_content" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Request Body:**
- `url` (string, optional): URL to extract content from
- `wait_for_element` (string, optional): CSS selector to wait for

### Summarize
Summarize text using a local LLM.

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text to summarize...", "max_tokens": 200}'
```

**Request Body:**
- `text` (string, required): Text to summarize
- `max_tokens` (integer, optional): Maximum tokens in summary (default: 200)

### Crawl
Crawl a website with depth control (placeholder implementation).

```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_depth": 2}'
```

**Request Body:**
- `url` (string, required): Starting URL
- `max_depth` (integer, optional): Maximum crawl depth (default: 2)

## Docker Support

Build and run with Docker:

```bash
docker-compose up -d
```

## Requirements

- Python 3.8+
- Playwright
- FastAPI
- BeautifulSoup4
- llama-cpp-python (for summarization)
- SearXNG instance (for web search)

## Unified Browser Tool Endpoint

The API provides a unified `/browser_tool` endpoint that handles multiple actions through a single interface. This is ideal for integration with llama-server.

### Usage Examples

**Search the web:**
```bash
curl -X POST "http://localhost:8000/browser_tool" \
  -H "Content-Type: application/json" \
  -d '{"action": "search", "query": "Python tutorials", "max_results": 5}'
```

**Get page content:**
```bash
curl -X POST "http://localhost:8000/browser_tool" \
  -H "Content-Type: application/json" \
  -d '{"action": "get_page", "url": "https://example.com"}'
```

**Summarize text:**
```bash
curl -X POST "http://localhost:8000/browser_tool" \
  -H "Content-Type: application/json" \
  -d '{"action": "summarize", "text": "Long text to summarize...", "max_tokens": 200}'
```

## Integration with llama-server

Create a `tools.yaml` file for llama-server integration:

```yaml
tools:
  - name: browser
    description: >
      Use this tool to search the web, fetch a web page, or summarize text content.
    parameters:
      type: object
      properties:
        action:
          type: string
          description: One of 'search', 'get_page', or 'summarize'.
          enum: [search, get_page, summarize]
        query:
          type: string
          description: Search term for 'search' action.
        url:
          type: string
          description: Web page URL for 'get_page' action.
        text:
          type: string
          description: Text to summarize for 'summarize' action.
        max_results:
          type: integer
          description: Maximum number of search results (default 10).
          default: 10
        max_tokens:
          type: integer
          description: Maximum tokens for summarization (default 200).
          default: 200
      required: [action]
    endpoint: http://localhost:8000/browser_tool
```

### Start llama-server with tools

```bash
llama-server \
  --model /path/to/your/model.gguf \
  --tools-file tools.yaml \
  --host 0.0.0.0 \
  --port 8080
```

The LLM will now be able to:
- Search the web for information
- Fetch and extract content from web pages
- Summarize long texts

## Notes

- The web search feature requires a running SearXNG instance
- The summarization feature requires a local LLM model in GGUF format
- Browser instances are automatically managed and cleaned up after each request
- The unified `/browser_tool` endpoint is recommended for llama-server integration
- Individual endpoints (`/web_search`, `/extract_content`, etc.) are still available for direct API usage
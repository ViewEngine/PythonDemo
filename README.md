# ViewEngine Python Demo

A demonstration of how to use ViewEngine's REST API with Python.

## Requirements

- Python 3.7 or higher
- `requests` library
- A ViewEngine API key

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Or install `requests` directly:

```bash
pip install requests
```

## Usage

Run the demo with your API key:

```bash
# Option 1: Provide API key as argument
python viewengine_demo.py YOUR_API_KEY_HERE

# Option 2: Run without arguments and you'll be prompted
python viewengine_demo.py
```

Make the script executable (Unix/Linux/Mac):

```bash
chmod +x viewengine_demo.py
./viewengine_demo.py YOUR_API_KEY_HERE
```

## What This Demo Does

1. **Discovers MCP Tools**: Lists available ViewEngine API endpoints
2. **Submits Retrieval Request**: Sends a URL to be retrieved
3. **Polls for Results**: Checks the status until completion
4. **Downloads Content**: Optionally downloads the retrieved page data

## Features Demonstrated

- ✅ API authentication with API keys
- ✅ MCP tools discovery endpoint
- ✅ Submitting retrieval requests
- ✅ Polling for job completion
- ✅ Handling different processing modes (Private/Community)
- ✅ Force refresh (bypass cache)
- ✅ Downloading retrieved content
- ✅ Type hints for better code clarity
- ✅ Proper error handling and exception management

## Configuration

Edit the `API_BASE_URL` constant in `viewengine_demo.py` to point to your ViewEngine instance:

```python
API_BASE_URL = "https://www.viewengine.io"  # Production
# API_BASE_URL = "http://localhost:5072"    # Local development
```

## Getting an API Key

1. Sign up at https://www.viewengine.io
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy the key (it's only shown once!)

## Example Output

```
╔══════════════════════════════════════════════════════════╗
║          ViewEngine REST API Demo (Python)              ║
║  Demonstrates using the MCP endpoints with an API key   ║
╚══════════════════════════════════════════════════════════╝

🔍 Step 1: Discovering available MCP tools...

✅ Found 2 available tools:
   • retrieve: Retrieve web page content
   • retrieve_status: Check status of retrieval request

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter a URL to retrieve (or press Enter for example.com): https://example.com

Force fresh retrieval? (y/n, default: n - use cache if available): n

Processing mode (private/community, default: private): private

🌐 Step 2: Submitting retrieval request for https://example.com...
   (Will use cached results if available)
   Mode: private

✅ Request submitted successfully!
   Request ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
   Status: queued
   Estimated wait: 30s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Step 3: Polling for results (this may take a while)...

   [1/60] Status: processing - Job assigned to feeder
   [2/60] Status: complete - Retrieval completed

✅ Retrieval completed!
   Status: complete
   URL: https://example.com
   Completed at: 2025-01-10T12:34:56Z

📄 Content available:
   Page Data URL: https://www.viewengine.io/v1/mcp/content/xyz123
   Content Hash: abc123def456
   Artifacts: screenshot, pdf
   Metrics: loadTime, pageSize

Download page content? (y/n): y

⬇️  Downloading page content...

📄 Page Content (first 500 chars):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "html": "<!DOCTYPE html><html>...",
  "title": "Example Domain",
  "url": "https://example.com",
  "normalizedText": "Example Domain This domain is for use..."
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Demo completed successfully!
```

## API Endpoints Used

- `GET /v1/mcp/tools` - List available MCP tools
- `POST /v1/mcp/retrieve` - Submit retrieval request
- `GET /v1/mcp/retrieve/{id}` - Check retrieval status
- `GET /v1/mcp/content/{id}` - Download retrieved content

## Error Handling

The demo includes error handling for:
- Invalid API keys
- Network failures
- Timeout scenarios
- Failed retrievals
- Invalid responses
- HTTP errors with detailed messages

## Integration Example

Here's how to integrate ViewEngine into your Python application:

```python
import requests

class ViewEngineClient:
    def __init__(self, api_key: str, base_url: str = "https://www.viewengine.io"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def retrieve_url(self, url: str, mode: str = "private") -> dict:
        """Retrieve a URL and return the content"""
        # Submit request
        response = self.session.post(
            f"{self.base_url}/v1/mcp/retrieve",
            json={"url": url, "mode": mode}
        )
        response.raise_for_status()
        data = response.json()

        # Poll for completion
        request_id = data["requestId"]
        while True:
            status_response = self.session.get(
                f"{self.base_url}/v1/mcp/retrieve/{request_id}"
            )
            status_response.raise_for_status()
            result = status_response.json()

            if result["status"] == "complete":
                return result
            elif result["status"] in ["failed", "canceled"]:
                raise Exception(f"Retrieval failed: {result.get('error')}")

            time.sleep(2)

# Usage
client = ViewEngineClient("your-api-key-here")
result = client.retrieve_url("https://example.com")
print(result)
```

## Support

For questions or issues:
- Documentation: https://www.viewengine.io/docs
- GitHub: https://github.com/viewengine
- Code Samples: https://github.com/viewengine
- Email: dev@viewengine.io

## License

See the main ViewEngine repository for license information.

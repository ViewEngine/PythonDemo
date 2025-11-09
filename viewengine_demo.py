#!/usr/bin/env python3
"""
ViewEngine REST API Demo (Python)
Demonstrates using the MCP endpoints with an API key

Usage:
    python viewengine_demo.py <api-key>
    OR
    python viewengine_demo.py (you'll be prompted for the API key)
"""

import sys
import json
import time
import requests
from typing import Optional, List, Dict, Any

API_BASE_URL = "https://www.viewengine.io"
# API_BASE_URL = "http://localhost:5072"  # For local development


class ViewEngineDemo:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def run(self) -> None:
        """Main entry point for the demo"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          ViewEngine REST API Demo (Python)              ║")
        print("║  Demonstrates using the MCP endpoints with an API key   ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()

        try:
            self.run_demo()
        except Exception as e:
            print(f"❌ Error: {e}\n")
            print("Stack trace:")
            import traceback
            traceback.print_exc()

        print("\nPress Enter to exit...")
        input()

    def run_demo(self) -> None:
        """Run the full demo workflow"""
        print("🔍 Step 1: Discovering available MCP tools...\n")

        tools = self.get_mcp_tools()
        if tools:
            print(f"✅ Found {len(tools)} available tools:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
        else:
            print("⚠️  No tools found or API not responding")

        print("\n" + "━" * 60 + "\n")

        # Get URL to retrieve
        url = input("Enter a URL to retrieve (or press Enter for example.com): ").strip()
        if not url:
            url = "https://example.com"

        force_refresh_input = input(
            "\nForce fresh retrieval? (y/n, default: n - use cache if available): "
        ).strip().lower()
        force_refresh = force_refresh_input == "y"

        mode_input = input(
            "\nProcessing mode (private/community, default: private): "
        ).strip().lower()
        mode = "community" if mode_input == "community" else "private"

        print(f"\n🌐 Step 2: Submitting retrieval request for {url}...")
        if force_refresh:
            print("   (Forcing fresh retrieval, bypassing cache)")
        else:
            print("   (Will use cached results if available)")
        print(f"   Mode: {mode}\n")

        retrieve_response = self.submit_retrieve_request(url, force_refresh, mode)
        if not retrieve_response:
            print("❌ Failed to submit retrieval request")
            return

        print("✅ Request submitted successfully!")
        print(f"   Request ID: {retrieve_response['requestId']}")
        print(f"   Status: {retrieve_response['status']}")
        print(f"   Estimated wait: {retrieve_response['estimatedWaitTimeSeconds']}s")

        print("\n" + "━" * 60 + "\n")
        print("⏳ Step 3: Polling for results (this may take a while)...\n")

        result = self.poll_for_results(retrieve_response["requestId"])
        if not result:
            print("❌ Failed to get results")
            return

        print("✅ Retrieval completed!")
        print(f"   Status: {result['status']}")
        print(f"   URL: {result['url']}")
        print(f"   Completed at: {result.get('completedAt', 'N/A')}")

        if result.get("content"):
            content = result["content"]
            print("\n📄 Content available:")
            print(f"   Page Data URL: {content['pageDataUrl']}")
            print(f"   Content Hash: {content.get('contentHash', 'N/A')}")

            if content.get("artifacts"):
                print(f"   Artifacts: {', '.join(content['artifacts'].keys())}")

            if content.get("metrics"):
                print(f"   Metrics: {', '.join(content['metrics'].keys())}")

            download = input("\nDownload page content? (y/n): ").strip().lower()
            if download == "y":
                self.download_page_data(content["pageDataUrl"])

        print("\n" + "━" * 60 + "\n")
        print("✅ Demo completed successfully!")

    def get_mcp_tools(self) -> Optional[List[Dict[str, str]]]:
        """Get available MCP tools from the API"""
        try:
            response = self.session.get(f"{API_BASE_URL}/v1/mcp/tools")
            response.raise_for_status()
            data = response.json()
            return data.get("tools")
        except Exception as e:
            print(f"Error getting tools: {e}")
            return None

    def submit_retrieve_request(
        self, url: str, force_refresh: bool, mode: str
    ) -> Optional[Dict[str, Any]]:
        """Submit a retrieval request"""
        try:
            request_body = {
                "url": url,
                "timeoutSeconds": 60,
                "forceRefresh": force_refresh,
                "mode": mode,
            }

            response = self.session.post(
                f"{API_BASE_URL}/v1/mcp/retrieve",
                json=request_body,
                headers={"Content-Type": "application/json"},
            )

            if not response.ok:
                print(f"API Error ({response.status_code}): {response.text}")
                return None

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error submitting retrieval request: {e}")
            return None

    def poll_for_results(
        self, request_id: str, max_attempts: int = 60
    ) -> Optional[Dict[str, Any]]:
        """Poll for retrieval results"""
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.get(
                    f"{API_BASE_URL}/v1/mcp/retrieve/{request_id}"
                )
                response.raise_for_status()
                result = response.json()

                if not result:
                    print(f"   [{attempt}/{max_attempts}] Failed to deserialize response")
                    time.sleep(2)
                    continue

                status = result.get("status", "unknown")
                message = result.get("message", "")
                print(f"   [{attempt}/{max_attempts}] Status: {status} - {message}")

                if status == "complete":
                    return result

                if status in ["failed", "canceled"]:
                    error = result.get("error", "Unknown error")
                    print(f"   Error: {error}")
                    return result

                time.sleep(2)
            except Exception as e:
                print(f"   [{attempt}/{max_attempts}] Error: {e}")
                time.sleep(2)

        print("⚠️  Timeout: Maximum polling attempts reached")
        return None

    def download_page_data(self, page_data_url: str) -> None:
        """Download and display page data"""
        try:
            print("\n⬇️  Downloading page content...")

            response = self.session.get(page_data_url)
            response.raise_for_status()
            page_data = response.json()

            print("\n📄 Page Content (first 500 chars):")
            print("━" * 60)

            pretty_json = json.dumps(page_data, indent=2)
            if len(pretty_json) > 500:
                print(pretty_json[:500] + "...")
            else:
                print(pretty_json)

            print("━" * 60)
        except Exception as e:
            print(f"Error downloading page data: {e}")


def main():
    """Main entry point"""
    api_key = None

    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your API key: ").strip()

    if not api_key:
        print("❌ Error: API key is required\n")
        print("Usage:")
        print("  python viewengine_demo.py <api-key>")
        print("  OR")
        print("  python viewengine_demo.py   (you'll be prompted for the API key)")
        sys.exit(1)

    demo = ViewEngineDemo(api_key)
    demo.run()


if __name__ == "__main__":
    main()

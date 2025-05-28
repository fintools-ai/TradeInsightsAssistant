import asyncio
import json
import sys
from datetime import datetime


async def run_mcp_tool():
    # Update with the actual path to your tool script
    cmd = [
        sys.executable,  # This uses the same Python interpreter
        "mcp-openinterest-server"  # or "run_server.py" depending on your layout
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def read_stdout_until_ready():
        while True:
            line = await process.stdout.readline()
            if not line:
                raise Exception("No output from tool")
            decoded = line.decode().strip()
            try:
                msg = json.loads(decoded)
                if msg.get("method") == "server/ready":
                    print("✅ Tool is ready")
                    return
            except json.JSONDecodeError:
                print(f"(non-JSON stdout): {decoded}")

    async def send_request_and_get_response(payload: dict):
        request_str = json.dumps(payload) + "\n"
        process.stdin.write(request_str.encode())
        await process.stdin.drain()

        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
        return json.loads(response_line.decode())

    try:
        await read_stdout_until_ready()

        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "TestClient",
                    "version": "0.1"
                }
            },
            "id": 1
        }
        init_response = await send_request_and_get_response(init_request)
        print("Initialization response:", json.dumps(init_response, indent=2))

        # Step 2: Call your tool
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "analyze_open_interest",
                "arguments": {
                    "ticker": "SPY",
                    "days": 3,
                    "include_news": False
                }
            },
            "id": 2
        }
        call_response = await send_request_and_get_response(call_request)
        print("Tool response:")
        print(json.dumps(call_response, indent=2)[:2000])  # Truncate if long

    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(run_mcp_tool())

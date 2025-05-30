#!/usr/bin/env python3
"""Test MCP server standalone to verify it works properly."""

import asyncio
import json

async def test_mcp_server():
    """Test the MCP server with direct JSON-RPC communication."""
    
    print("Starting MCP server...")
    
    # Start the MCP server
    process = await asyncio.create_subprocess_exec(
        "mcp-openinterest-server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=100 * 1024 * 1024  # 100MB limit
    )
    
    # Monitor stderr in background
    async def read_stderr():
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            print(f"[STDERR] {line.decode().strip()}")
    
    asyncio.create_task(read_stderr())
    
    # Wait for server to start
    await asyncio.sleep(1)
    
    try:
        # Initialize
        print("\n1. Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "0.1.0"
                }
            },
            "id": 1
        }
        
        request_str = json.dumps(init_request) + "\n"
        process.stdin.write(request_str.encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
        response = json.loads(response_line.decode())
        print(f"Initialize response: {json.dumps(response, indent=2)}")
        
        # Send initialized notification
        print("\n2. Sending initialized notification...")
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        request_str = json.dumps(initialized_request) + "\n"
        process.stdin.write(request_str.encode())
        await process.stdin.drain()
        
        await asyncio.sleep(0.5)
        
        # List tools
        print("\n3. Listing tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        request_str = json.dumps(list_tools_request) + "\n"
        process.stdin.write(request_str.encode())
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
        response = json.loads(response_line.decode())
        print(f"Tools list response: {json.dumps(response, indent=2)}")
        
        # Test a simple call - just 1 day
        print("\n4. Testing analyze_open_interest for SPY with 1 day...")
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "analyze_open_interest",
                "arguments": {
                    "ticker": "SPY",
                    "days": 1
                }
            },
            "id": 3
        }
        
        request_str = json.dumps(tool_request) + "\n"
        process.stdin.write(request_str.encode())
        await process.stdin.drain()
        
        print("Waiting for response (timeout: 60s)...")
        start_time = asyncio.get_event_loop().time()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=60)
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"Response received in {elapsed:.2f} seconds")
            
            response = json.loads(response_line.decode())
            
            # Check if it's an error
            if "error" in response:
                print(f"Error response: {json.dumps(response['error'], indent=2)}")
            else:
                # Print summary of response
                result = response.get("result", {})
                content = result.get("content", [])
                if content and "text" in content[0]:
                    data = json.loads(content[0]["text"])
                    print(json.dumps(data, indent=2))
                    
                else:
                    print(f"Unexpected response format: {json.dumps(response, indent=2)}")
                    
        except asyncio.TimeoutError:
            print(f"TIMEOUT after 60 seconds!")
            print("Trying to read any partial data...")
            try:
                partial = await asyncio.wait_for(process.stdout.read(1024), timeout=1)
                if partial:
                    print(f"Partial data: {partial.decode()[:200]}...")
            except:
                print("No partial data available")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nTerminating server...")
        process.terminate()
        await process.wait()
        print("Server terminated")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())

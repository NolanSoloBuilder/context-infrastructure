#!/usr/bin/env python3
"""Run one mailbox MCP operation, then close the server and its connections."""

import argparse
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import sys


async def run(tool, arguments):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server = StdioServerParameters(
        command=str(Path.home() / ".local/bin/mcp-email-server"), args=["stdio"]
    )
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(
            reader, writer, read_timeout_seconds=timedelta(seconds=60)
        ) as session:
            await session.initialize()
            if tool is None:
                result = await session.list_tools()
            else:
                result = await session.call_tool(tool, arguments=arguments)
            print(result.model_dump_json(by_alias=True, exclude_none=True), flush=True)
            return bool(getattr(result, "isError", False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-tools", action="store_true")
    group.add_argument("--tool", help="Tool name; JSON arguments are read from stdin")
    args = parser.parse_args()
    worker_python = Path.home() / ".local/share/uv/tools/mcp-email-server/bin/python"
    try:
        import mcp  # noqa: F401
    except ImportError:
        if not worker_python.exists():
            parser.error("The installed mcp-email-server Python environment is missing")
        # Reuse the existing tool environment; do not install another SDK or server.
        os.execv(str(worker_python), [str(worker_python), __file__, *sys.argv[1:]])
    arguments = json.load(sys.stdin) if args.tool else None
    if arguments is not None and not isinstance(arguments, dict):
        parser.error("Tool arguments must be a JSON object")
    try:
        return int(asyncio.run(asyncio.wait_for(run(args.tool, arguments), timeout=90)))
    except (TimeoutError, KeyboardInterrupt):
        print("Mailbox request interrupted or timed out; no automatic retry.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

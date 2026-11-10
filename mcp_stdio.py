"""Minimal, dependency-free Model Context Protocol server over stdio.

Implements the subset of MCP needed by tool servers: initialize, ping,
tools/list and tools/call, using newline-delimited JSON-RPC 2.0 on
stdin/stdout. Logs go to stderr so stdout stays a clean protocol channel.
"""
from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Callable, Dict, List

SUPPORTED_PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]


class Tool:
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any],
                 handler: Callable[..., Any], read_only: bool = True):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
        self.read_only = read_only

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": {"readOnlyHint": self.read_only, "openWorldHint": True},
        }


class StdioServer:
    def __init__(self, name: str, version: str, instructions: str = ""):
        self.name = name
        self.version = version
        self.instructions = instructions
        self.tools: Dict[str, Tool] = {}

    def tool(self, name: str, description: str, input_schema: Dict[str, Any], read_only: bool = True):
        def decorator(fn: Callable[..., Any]):
            self.tools[name] = Tool(name, description, input_schema, fn, read_only)
            return fn
        return decorator

    # ---- protocol ---------------------------------------------------------
    def _result(self, msg_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def _error(self, msg_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}

    def handle(self, msg: Dict[str, Any]) -> Dict[str, Any] | None:
        method = msg.get("method")
        msg_id = msg.get("id")
        params = msg.get("params") or {}
        is_notification = "id" not in msg

        if method == "initialize":
            requested = params.get("protocolVersion")
            version = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else SUPPORTED_PROTOCOL_VERSIONS[0]
            result = {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": self.name, "version": self.version},
            }
            if self.instructions:
                result["instructions"] = self.instructions
            return self._result(msg_id, result)
        if method == "ping":
            return self._result(msg_id, {})
        if method == "tools/list":
            return self._result(msg_id, {"tools": [t.as_dict() for t in self.tools.values()]})
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            tool = self.tools.get(name)
            if tool is None:
                return self._error(msg_id, -32602, f"Unknown tool: {name}")
            try:
                output = tool.handler(**args)
                text = output if isinstance(output, str) else json.dumps(output, indent=2, ensure_ascii=False)
                return self._result(msg_id, {"content": [{"type": "text", "text": text}], "isError": False})
            except (TypeError, ValueError) as exc:
                return self._result(msg_id, {"content": [{"type": "text", "text": f"Invalid input: {exc}"}], "isError": True})
            except Exception as exc:  # report tool failures to the model instead of crashing
                print(traceback.format_exc(), file=sys.stderr)
                return self._result(msg_id, {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True})
        if is_notification:
            return None  # notifications/initialized, notifications/cancelled, etc.
        return self._error(msg_id, -32601, f"Method not found: {method}")

    def serve(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                self._write(self._error(None, -32700, "Parse error"))
                continue
            batch: List[Dict[str, Any]] = msg if isinstance(msg, list) else [msg]
            for item in batch:
                response = self.handle(item)
                if response is not None:
                    self._write(response)

    @staticmethod
    def _write(obj: Dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()

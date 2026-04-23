# MCP Studio

A hands-on sandbox for learning and experimenting with the **Model Context Protocol (MCP)** — the open standard that lets LLMs talk to external tools and data sources.

## What's inside

| File | Role |
|---|---|
| `server_01.py` | FastMCP server exposing a set of example tools |
| `client_01.py` | Async MCP client that spawns the server and exercises all tools |

### Tools exposed by the server

| Tool | Description |
|---|---|
| `add(a, b)` | Sums two integers |
| `multiply(a, b)` | Multiplies two floats |
| `greet(name)` | Returns a personalised greeting |
| `list_people(prefix, names_list)` | Strips a prefix from each name in a list |
| `word_stats(text)` | Returns word count, char counts, longest word, and average word length |

## Getting started

### 1. Create and activate the virtual environment

```bash
python3.11 -m venv py311env
source py311env/bin/activate   # Windows: py311env\Scripts\activate
```

### 2. Install dependencies

```bash
pip install mcp numpy
```

### 3. Run the client (it spawns the server automatically)

```bash
python client_01.py
```

### 4. Inspect the server interactively (optional)

```bash
mcp dev server_01.py
```

This opens the MCP Inspector in your browser so you can call tools manually.

## How it works

```
client_01.py
    │  spawns via stdio
    ▼
server_01.py  (FastMCP)
    │  registers tools via @mcp.tool()
    ▼
LLM / Inspector / any MCP-compatible host
```

The client and server communicate over **stdio transport** — the client gives birth to the server as a child process and they exchange JSON-RPC messages through stdin/stdout. No HTTP, no ports.

## Project structure

```
mcp-studio/
├── server_01.py   # MCP server with example tools
├── client_01.py   # MCP client with test calls
└── README.md
```

## References

- [Model Context Protocol specification](https://modelcontextprotocol.io)
- [FastMCP documentation](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

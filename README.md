# SQLite toolkit build with FastMCP for LLM/agents frontends such as LM-Studio

FastMCP-based SQLite toolkit that can perform most standard SQL queries such as SELECT, INSERT, UPDATE, DELETE, ALTER, JOIN, ect'.
Some of the simple or specific operation can performed via dedicated functions (tools) such as `insert_row()`, `update_rows()`, `delete_rows()`, `add_column()`, given explicit arguments. 
For complex queries or ones that are given entirely in natural language can be performed via raw SQL string with `execute_sql_query()`.
Designed to be used with via MCP protocol with LLMs frontends such as [LM Studio](https://lmstudio.ai).


## ✅ Features

- Most standard SQL-style queries can be performed
- Both simple and complex queries are executed via dedicated functions or via raw SQL string
- Prefer the dedicated functions when possible — they’re safer and easier to use.
- Use `execute_sql_query()` for advanced cases or when the dedicated functions don’t fit.
- Input validation with Pydantic scheme
- Works seamlessly with LM Studio via MCP protocol

## 🚀 Installation

Install directly from GitHub:

```
pip install git+https://github.com/VadimDu/sqlite-toolkit-mcp.git
```

Or install in development mode:

```
git clone https://github.com/VadimDu/sqlite-toolkit-mcp.git
cd pdf-tool
pip install -e .
```

## 🛠 Testing

To test the this mcp-tool before real usage by LLM/agent:
```
python -m sqlite_tool.sqlite_tool_mcp_server
```
or
```
fastmcp run sqlite_tool/sqlite_tool_mcp_server.py
```
If everything is working fine, you should see a message like this:
`[date time] INFO     Starting MCP server 'SQLite-tool' with transport 'stdio'`

## 🎉 Usage in LM Studio

Add the following to your `mcp.json` file:
```
{
  "sqlite-tool_1": {
    "command": "python",
    "args": [
      "-m", "sqlite_tool.sqlite_tool_mcp_server",
      "--db-path", "B:\Tester_control\Tester_tasks.sqlite"
    ]
  }
}
```

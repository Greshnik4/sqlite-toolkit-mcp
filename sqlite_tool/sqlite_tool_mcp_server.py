#!/usr/bin/env python3
"""
SQLite MCP Tool — single-database edition.
DB path is supplied once at server startup via CLI argument or env variable.
"""

import os
import sys
import logging
import sqlite3
from fastmcp import FastMCP
from typing import List, Dict, Any

# ── Logger ──────────────────────────────────────────────────────────────
logger = logging.getLogger("SQLite-tool")
logging.basicConfig(level=logging.INFO)

# ── Read DB path from CLI arg (--db-path) or env var SQLITE_DB_PATH ────
def _resolve_db_path() -> str:
    # 1) Try CLI argument:  python -m sqlite_tool.sqlite_tool_mcp_server --db-path /path/to.db
    if "--db-path" in sys.argv:
        idx = sys.argv.index("--db-path")
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    # 2) Try environment variable
    env = os.environ.get("SQLITE_DB_PATH")
    if env:
        return env
    # 3) Fallback
    logger.error("No DB path provided. Use --db-path <path> or set SQLITE_DB_PATH env var.")
    sys.exit(1)

DB_PATH: str = _resolve_db_path()
logger.info(f"Using SQLite database: {DB_PATH}")

# ── FastMCP server ─────────────────────────────────────────────────────
mcp = FastMCP("SQLite-tool")


# ── Helper: open a connection ──────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


# ── Tools ──────────────────────────────────────────────────────────────

@mcp.tool(description="Execute a SQL query on the SQLite database.")
def execute_sql_query(query: str) -> List[Dict[str, Any]]:
    """Execute raw SQL. Returns list of dicts for SELECT, or row count otherwise."""
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.commit()
        return [{"rows_affected": cur.rowcount}]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="Get the schema of all tables in the database.")
def get_database_schema() -> List[Dict[str, Any]]:
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cur.fetchall()
        schema = []
        for (tname,) in tables:
            cur.execute(f"PRAGMA table_info({tname});")
            schema.append({
                "table": tname,
                "columns": [
                    {"name": c[1], "type": c[2],
                     "notnull": bool(c[3]), "default": c[4], "primary_key": bool(c[5])}
                    for c in cur.fetchall()
                ]
            })
        return schema
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="List all table names in the database.")
def list_tables() -> List[str]:
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        return [r[0] for r in cur.fetchall()]
    except Exception as e:
        return [f"error: {e}"]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="Insert a single row into a table.")
def insert_row(table: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not data:
        return [{"error": "No data provided"}]
    cols = list(data.keys())
    placeholders = ", ".join("?" for _ in cols)
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(sql, list(data.values()))
        conn.commit()
        return [{"inserted_id": cur.lastrowid}]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="Update rows in a table with WHERE conditions.")
def update_rows(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not data or not where:
        return [{"error": "Both 'data' and 'where' must be provided"}]
    set_clause = ", ".join(f"{c} = ?" for c in data)
    where_clause = " AND ".join(f"{c} = ?" for c in where)
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(sql, list(data.values()) + list(where.values()))
        conn.commit()
        return [{"rows_affected": cur.rowcount}]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="Delete rows from a table with WHERE conditions.")
def delete_rows(table: str, where: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not where:
        return [{"error": "'where' condition required"}]
    where_clause = " AND ".join(f"{c} = ?" for c in where)
    sql = f"DELETE FROM {table} WHERE {where_clause}"
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(sql, list(where.values()))
        conn.commit()
        return [{"rows_affected": cur.rowcount}]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


@mcp.tool(description="Add a new column to an existing table.")
def add_column(table: str, column_name: str, data_type: str) -> List[Dict[str, Any]]:
    allowed = {"TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB", "DATE", "DATETIME"}
    if data_type.upper() not in allowed:
        return [{"error": f"data_type must be one of: {', '.join(allowed)}"}]
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {data_type}")
        conn.commit()
        return [{"success": True, "message": f"Column '{column_name}' added to '{table}'"}]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if "conn" in locals():
            conn.close()


# ── Entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()

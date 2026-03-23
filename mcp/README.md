# OpenGIN MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides access to the **OpenGIN Knowledge Graph**. 

This server acts as a bridge between LLMs (like Claude Desktop) and the OpenGIN Read API, allowing AI assistants to query government structures, ministerial appointments, and tabular datasets from Sri Lanka's public records.

## Features

- 📂 **Graph Traversal**: Explore relationships between government entities, ministers, and departments.
- 🔍 **Universal Search**: Find entities by name, kind, or date.
- 📊 **Tabular Data Access**: Fetch specific attributes and dataset rows with field-level filtering.
- 📜 **Schema Exposure**: Built-in schema resource allows the LLM to learn the graph structure dynamically.

## Installation

### Prerequisites
- Python 3.11 or higher
- Access to an OpenGIN Read API instance (default: `http://localhost:8081/v1`)

### Setup
1. Clone this repository and navigate to the root directory.
2. Create a virtual environment and install the dependencies:
   ```bash
   pip install -e .
   ```
3. Create a `.env` file in the root directory (using `env.example` as a template):
   ```bash
   cp env.example .env
   ```
4. Update `OPENGIN_READ_API_URL` if your API is running somewhere other than localhost.

## Configuration

The server reads the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENGIN_READ_API_URL` | `http://localhost:8081/v1` | Base URL of the Read API |

## Capabilities

### Tools
- **`search_entities`**: Find entity IDs by filtering for `kind`, `name`, or `date`.
- **`get_entity_metadata`**: Fetch the basic record/metadata for a specific entity ID.
- **`get_entity_attribute`**: Query tabular dataset attributes (like appointments or categories) with row/column filters.
- **`get_entity_relations`**: Browse outgoing or incoming relationships (e.g., "who is appointed to this ministry?").

### Resources
- **`opengin://schema`**: Returns the complete OpenGIN Knowledge Graph schema, including entity kinds and relationship types.

## Usage with Claude Desktop

To use this with Claude Desktop, add a new entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "opengin": {
      "command": "opengin-mcp",
      "cwd": "/absolute/path/to/your/project"
    }
  }
}
```

(Note: If Claude Desktop says it can't find the `opengin-mcp` command, you might need to provide the full path to it. You can find this by running `which opengin-mcp` in your terminal and providing this path as the `command`.)

## Running the Server

### For Development and Testing
You can use the **MCP Inspector** to test your tools and resources in a browser-based UI:
```bash
npx @modelcontextprotocol/inspector opengin-mcp
```

### Development Mode (Auto-Reload)
If you have the `fastmcp` CLI tool installed, you can run the server in development mode, which watches for file changes:
```bash
fastmcp dev server.py
```


## Project Structure

- `server.py`: Main entry point initializing the FastMCP server.
- `client.py`: HTTP client for the OpenGIN Read API.
- `tools/`: Individual tool implementations (search, metadata, relations, etc.).
- `resources/`: KG schema definitions.
- `config.py`: Environment-based configuration management.

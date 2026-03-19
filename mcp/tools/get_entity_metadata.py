"""
MCP Tool: get_entity_metadata
Maps to GET /entities/{id}/metadata
"""
import json
import client as api


def register(mcp):
    @mcp.tool()
    def get_entity_metadata(entity_id: str) -> str:
        """
        Fetch the metadata document for a specific entity by its ID.

        Metadata is unstructured and varies by entity type — it may include descriptions,
        classifications, source references, or other administrative fields.

        Use `search_entities` first to get the entity ID if you only have a name.

        Inputs:
          - `entity_id` (required): the ID of the entity

        Returns a JSON object whose structure depends on the entity type.
        """
        try:
            result = api.get_entity_metadata(entity_id)
            return json.dumps(result, indent=2)
        except ValueError as e:
            return f"Error: {e}"

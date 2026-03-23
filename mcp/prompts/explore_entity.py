"""
MCP Prompt: explore_entity
Given an entity name and kind, find it, fetch its metadata, and survey its relationships.
"""


def register(mcp):
    @mcp.prompt()
    def explore_entity(name: str, kind_major: str, kind_minor: str = "") -> str:
        """
        Given an entity name and kind, find it, then fetch its metadata and key attributes.
        Use this as a starting point for exploring any entity in the knowledge graph.
        """
        kind_minor_clause = f' and kind_minor="{kind_minor}"' if kind_minor else ""
        return f"""You are exploring an entity in the OpenGIN knowledge graph.

    Steps:
    1. Call `search_entities` with kind_major="{kind_major}"{kind_minor_clause} and name="{name}" to find the entity ID.
    2. Call `get_entity_metadata` with the entity ID to understand what this entity is.
    3. Call `get_entity_relations` with the entity ID (no filters) to see what it is connected to.
    4. Summarise what you found: the entity's identity, metadata highlights, and key relationships.
    """

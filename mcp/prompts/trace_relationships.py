"""
MCP Prompt: trace_relationships
Walk the relationships of an entity recursively to map its connections.
"""


def register(mcp):
    @mcp.prompt()
    def trace_relationships(entity_id: str, direction: str = "OUTGOING", depth: int = 2) -> str:
        """
        Walk the relationships of an entity recursively to build a picture of its connections.
        """
        return f"""You are tracing the relationship graph starting from entity "{entity_id}".

    Steps:
    1. Call `get_entity_relations` with entity_id="{entity_id}" and direction="{direction}" to get its direct relationships.
    2. For each related entity returned, call `get_entity_relations` on that entity (up to {depth} levels deep).
    3. Build a summary of how these entities are connected — list each hop and the relationship name connecting them.
    4. Identify any notable patterns (e.g. a person connected to multiple ministries, or a department with many datasets).
    """

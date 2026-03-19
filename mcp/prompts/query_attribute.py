"""
MCP Prompt: query_attribute
Handles the full search → attribute fetch chain for a named entity and attribute.
"""


def register(mcp):
    @mcp.prompt()
    def query_attribute(
        entity_name: str,
        kind_major: str,
        attribute_name: str,
        start_time: str = "",
        end_time: str = "",
    ) -> str:
        """
        Given an entity name and attribute name, handle the full search → fetch chain automatically.
        """
        time_clause = ""
        if start_time or end_time:
            time_clause = f', start_time="{start_time}", end_time="{end_time}"'

        return f"""You are retrieving attribute data from the OpenGIN knowledge graph.

    Steps:
    1. Call `search_entities` with kind_major="{kind_major}" and name="{entity_name}" to find the entity ID.
    2. Call `get_entity_attribute` with the entity ID, attribute_name="{attribute_name}"{time_clause}.
    3. Summarise the result clearly — mention the time periods covered and the key values returned.
    """

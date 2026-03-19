from . import search_entities, get_entity_metadata, get_entity_attribute, get_entity_relations


def register_all(mcp):
    search_entities.register(mcp)
    get_entity_metadata.register(mcp)
    get_entity_attribute.register(mcp)
    get_entity_relations.register(mcp)

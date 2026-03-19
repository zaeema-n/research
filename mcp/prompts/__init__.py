from . import explore_entity, trace_relationships, query_attribute


def register_all(mcp):
    explore_entity.register(mcp)
    trace_relationships.register(mcp)
    query_attribute.register(mcp)

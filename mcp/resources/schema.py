"""
MCP Resource: opengin://schema
Exposes the OpenGIN knowledge graph schema so the LLM can understand
entity kinds, relationship types, and graph structure before querying.
"""

CONTENT = """
# OpenGIN Knowledge Graph Schema

## Root
The root of the entire graph is a single entity:
  Name: "Government of Sri Lanka"
  Kind: Organisation/government

All other entities are reachable from this root via relationships.

## Entity Kinds (major/minor)

| Major        | Minor             | Description |
|--------------|-------------------|-------------|
| Category     | parentCategory    | A top-level category node grouping datasets |
| Category     | childCategory     | A sub-category, can nest arbitrarily deep |
| Dataset      | tabular           | A tabular dataset stored in PostgreSQL; queryable with row/column filters |
| Document     | extgztperson      | A person entry from the Gazette (external document) |
| Document     | extgztorg         | An organisation entry from the Gazette (external document) |
| Organisation | department        | A government department under a minister |
| Organisation | cabinetMinister   | A Cabinet Minister entity |
| Organisation | government        | The root government entity |
| Organisation | stateMinister     | A State Minister entity |
| Person       | citizen           | A citizen of Sri Lanka |

## Graph Hierarchy

  government
    └── citizen (AS_MINISTER / AS_PRESIDENT / AS_PRIME_MINISTER)
          └── cabinetMinister / stateMinister (AS_APPOINTED)
                └── department (AS_DEPARTMENT)
                      └── citizen
                cabinetMinister / stateMinister
                      └── parentCategory (AS_CATEGORY)
                            └── childCategory → childCategory → ... → tabular (Dataset)
                department
                      └── parentCategory (AS_CATEGORY)
                            └── childCategory → childCategory → ... → tabular (Dataset)
    └── extgztperson / extgztorg (AS_DOCUMENT)
          └── extgztperson / extgztorg (REFERS_TO / MERGED_INTO)

## Relationship Types

| Relationship      | Meaning |
|-------------------|---------|
| AS_APPOINTED      | A citizen was appointed as a minister/state minister |
| AS_CATEGORY       | Links a minister or department to a category node |
| AS_DEPARTMENT     | A minister oversees a department |
| AS_DOCUMENT       | Links to an external Gazette document |
| AS_MINISTER       | A citizen holds a minister role |
| AS_PRESIDENT      | A citizen holds the presidency |
| AS_PRIME_MINISTER | A citizen holds the prime minister role |
| AMENDS            | One document/entity amends another |
| IS_ATTRIBUTE      | Links a tabular dataset as an attribute of an entity |
| MERGED_INTO       | An entity was merged into another |
| REFERS_TO         | An entity references another |
| RENAMED_TO        | An entity was renamed to another |

## Querying Tips

- Always start with `search_entities` to find the entity ID before fetching attributes or relationships.
- To find all ministers, search for kind.major = "Organisation" and kind.minor = "cabinetMinister" or "stateMinister".
- To find datasets under a minister or department, traverse: entity → AS_CATEGORY → parentCategory → childCategory → ... → tabular.
- Use direction = "OUTGOING" to follow a relationship forward, "INCOMING" to find what points to an entity.
- Tabular datasets (Dataset/tabular) can be filtered with row-level `records` filters and column `fields` selectors.
"""


def register(mcp):
    @mcp.resource("opengin://schema")
    def get_schema() -> str:
        """The OpenGIN knowledge graph schema — entity kinds, relationships, and graph hierarchy."""
        return CONTENT

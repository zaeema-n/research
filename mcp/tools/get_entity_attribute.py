"""
MCP Tool: get_entity_attribute
Maps to POST /entities/{id}/attributes/{name}
"""
import json
from typing import Any
import client as api


def _format_response(result: Any) -> str:
    """Prepend a summary line for tabular attribute data."""
    if isinstance(result, list):
        summary_parts = [f"{len(result)} time period(s) returned."]
        first_value = result[0].get("value") if result else None
        if isinstance(first_value, list) and first_value:
            cols = list(first_value[0].keys()) if isinstance(first_value[0], dict) else []
            if cols:
                summary_parts.append(f"Columns: {', '.join(cols)}")
        return "\n".join(summary_parts) + "\n\n" + json.dumps(result, indent=2)
    return json.dumps(result, indent=2)


def register(mcp):
    @mcp.tool()
    def get_entity_attribute(
        entity_id: str,
        attribute_name: str,
        start_time: str | None = None,
        end_time: str | None = None,
        fields: list[str] | None = None,
        records: list[dict] | None = None,
    ) -> str:
        """
        Retrieve the value(s) of a named attribute for a specific entity, optionally filtered
        by time range or row-level conditions.

        Attributes hold time-versioned data — the same attribute can have different values across
        different time periods (e.g. a ministry's budget each year).

        Use `search_entities` first to get the entity ID if you only have a name.

        Inputs:
          - `entity_id` (required): ID of the entity
          - `attribute_name` (required): name of the attribute (e.g. "budget", "population", "members")
          - `start_time` (optional): ISO 8601 — return values valid from this time
          - `end_time` (optional): ISO 8601 — return values valid until this time
          - `fields` (optional): list of column names to return for tabular data; defaults to all columns
          - `records` (optional): list of row-level filters for tabular data, each with:
              - `field_name`: the column to filter on
              - `operator`: one of eq, neq, gt, lt, gte, lte, contains, notcontains
              - `value`: the value to compare against

        Returns one or more time-based values, each with: start, end, value.
        If the attribute is tabular, `value` will contain rows and columns.
        Use `fields` to limit columns and `records` to filter rows.
        """
        try:
            result = api.get_entity_attribute(
                entity_id,
                attribute_name,
                start_time=start_time,
                end_time=end_time,
                fields=fields,
                records=records,
            )
            return _format_response(result)
        except ValueError as e:
            return f"Error: {e}"

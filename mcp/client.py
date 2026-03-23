"""
HTTP client for the OpenGIN Read API.
Each function maps to one API endpoint.
"""

import logging
from typing import Any

import httpx

from config import OPENGIN_READ_API_URL, REQUEST_TIMEOUT
from utils import decode_protobuf_name, decode_attribute_value, handle_response

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool: search_entities
# POST /entities/search
# ---------------------------------------------------------------------------

def search_entities(
    *,
    id: str | None = None,
    kind_major: str | None = None,
    kind_minor: str | None = None,
    name: str | None = None,
    created: str | None = None,
    terminated: str | None = None,
) -> Any:
    body: dict = {}
    if id:
        body["id"] = id
    else:
        if not kind_major:
            raise ValueError("search_entities: either `id` or `kind_major` is required")
        body["kind"] = {"major": kind_major}
        if kind_minor:
            body["kind"]["minor"] = kind_minor
        if name:
            body["name"] = name
        if created:
            body["created"] = created
        if terminated:
            body["terminated"] = terminated

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(f"{OPENGIN_READ_API_URL}/entities/search", json=body)

    result = handle_response(response, "search_entities")
    for item in result.get("body", []):
        if "name" in item:
            item["name"] = decode_protobuf_name(item["name"])
    return result


# ---------------------------------------------------------------------------
# Tool: get_entity_metadata
# GET /entities/{id}/metadata
# ---------------------------------------------------------------------------

def get_entity_metadata(entity_id: str) -> Any:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(f"{OPENGIN_READ_API_URL}/entities/{entity_id}/metadata")

    result = handle_response(response, "get_entity_metadata")
    if isinstance(result, dict) and "name" in result:
        result["name"] = decode_protobuf_name(result["name"])
    return result


# ---------------------------------------------------------------------------
# Tool: get_entity_attribute
# GET /entities/{id}/attributes/{name}
# ---------------------------------------------------------------------------

def get_entity_attribute(
    entity_id: str,
    attribute_name: str,
    *,
    start_time: str | None = None,
    end_time: str | None = None,
    fields: list[str] | None = None,
) -> Any:
    params: dict = {}
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time
    if fields:
        params["fields"] = fields

    url = f"{OPENGIN_READ_API_URL}/entities/{entity_id}/attributes/{attribute_name}"
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(url, params=params)

    result = handle_response(response, "get_entity_attribute")
    if isinstance(result, dict) and "value" in result:
        result["value"] = decode_attribute_value(result["value"])
    return result


# ---------------------------------------------------------------------------
# Tool: get_entity_relations
# POST /entities/{id}/relations
# ---------------------------------------------------------------------------

def get_entity_relations(
    entity_id: str,
    *,
    id: str | None = None,
    related_entity_id: str | None = None,
    name: str | None = None,
    direction: str | None = None,
    active_at: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> Any:
    if active_at and (start_time or end_time):
        raise ValueError(
            "get_entity_relations: `active_at` and `start_time`/`end_time` are "
            "mutually exclusive — use one or the other, not both."
        )

    body: dict = {}
    if id:
        body["id"] = id
    else:
        if related_entity_id:
            body["relatedEntityId"] = related_entity_id
        if name:
            body["name"] = name
        if direction:
            body["direction"] = direction
        if active_at:
            body["activeAt"] = active_at
        if start_time:
            body["startTime"] = start_time
        if end_time:
            body["endTime"] = end_time

    url = f"{OPENGIN_READ_API_URL}/entities/{entity_id}/relations"
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(url, json=body)

    result = handle_response(response, "get_entity_relations")
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and "name" in item:
                item["name"] = decode_protobuf_name(item["name"])
    return result

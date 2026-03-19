"""
HTTP client for the OpenGIN Read API.
Each function maps to one API endpoint.
"""
from typing import Any

import httpx

from config import OPENGIN_READ_API_URL, REQUEST_TIMEOUT


def _handle_response(response: httpx.Response, context: str) -> Any:
    """
    Raise a descriptive error if the response is not 2xx,
    otherwise return the parsed JSON body.
    """
    if response.status_code == 404:
        raise ValueError(f"{context}: entity not found (404)")
    if response.status_code == 400:
        detail = _safe_json(response).get("error", response.text)
        raise ValueError(f"{context}: bad request — {detail}")
    if not response.is_success:
        raise ValueError(
            f"{context}: API returned {response.status_code} — {response.text}"
        )
    return response.json()


def _safe_json(response: httpx.Response) -> dict:
    try:
        return response.json()
    except Exception:
        return {}


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
    return _handle_response(response, "search_entities")


# ---------------------------------------------------------------------------
# Tool: get_entity_metadata
# GET /entities/{id}/metadata
# ---------------------------------------------------------------------------

def get_entity_metadata(entity_id: str) -> Any:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(f"{OPENGIN_READ_API_URL}/entities/{entity_id}/metadata")
    return _handle_response(response, "get_entity_metadata")


# ---------------------------------------------------------------------------
# Tool: get_entity_attribute
# POST /entities/{id}/attributes/{name}
# ---------------------------------------------------------------------------

def get_entity_attribute(
    entity_id: str,
    attribute_name: str,
    *,
    start_time: str | None = None,
    end_time: str | None = None,
    fields: list[str] | None = None,
    records: list[dict] | None = None,
) -> Any:
    params: dict = {}
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    body: dict = {}
    if fields:
        body["fields"] = fields
    if records:
        body["records"] = records

    url = f"{OPENGIN_READ_API_URL}/entities/{entity_id}/attributes/{attribute_name}"
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(url, params=params, json=body)
    return _handle_response(response, "get_entity_attribute")


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
    return _handle_response(response, "get_entity_relations")

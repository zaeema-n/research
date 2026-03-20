"""
HTTP client for the OpenGIN Read API.
Each function maps to one API endpoint.
"""

import json
import binascii
import logging
from typing import Any

import httpx
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.struct_pb2 import Struct as ProtoStruct
from google.protobuf.json_format import MessageToDict

from config import OPENGIN_READ_API_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def decode_protobuf_name(name: str) -> str:
    """
    Decodes the protobuf-wrapped name returned by the OpenGIN API.
    Handles hex string -> bytes -> StringValue proto or raw UTF-8.
    If decoding fails, returns the original string to avoid data loss.
    """
    try:
        data = json.loads(name)
        hex_value = data.get("value")
        if not hex_value:
            logger.warning(f"Failed to decode name protobuf: {name}")
            return name

        decoded_bytes = binascii.unhexlify(hex_value)

        sv = StringValue()
        try:
            # Try parsing as a StringValue protobuf
            sv.ParseFromString(decoded_bytes)
            if sv.value.strip() == "":
                return decoded_bytes.decode("utf-8", errors="ignore").strip()
            return sv.value.strip()
        except Exception:
            # Fallback to UTF-8 decoding if not a valid proto string
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
            cleaned = "".join(ch for ch in decoded_str if ch.isprintable())
            return cleaned.strip()
    except Exception as e:
        logger.warning(f"Failed to decode name protobuf (Error: {e}): {name}")
        return name


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

    if not body:
        raise ValueError(
            "search_entities: at least one search parameter is required "
            "(id, kind_major, name, created, or terminated)."
        )

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(f"{OPENGIN_READ_API_URL}/entities/search", json=body)
    
    result = _handle_response(response, "search_entities")
    # Manually decode protobuf names if present
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
    
    result = _handle_response(response, "get_entity_metadata")
    if isinstance(result, dict) and "name" in result:
        result["name"] = decode_protobuf_name(result["name"])
    return result


# ---------------------------------------------------------------------------
# Tool: get_entity_attribute
# GET /entities/{id}/attributes/{name}
# ---------------------------------------------------------------------------

def decode_attribute_value(value: Any) -> Any:
    """
    Decode an attribute value returned by the OpenGIN API.

    The API wraps attribute values as a JSON string with shape:
        {"typeUrl": "type.googleapis.com/...", "value": "<hex>"}

    Supported typeUrls:
      - google.protobuf.Struct  → decoded to a plain Python dict
      - google.protobuf.StringValue → decoded via decode_protobuf_name

    Falls back to returning the raw value string on any error.
    """
    if not isinstance(value, str):
        return value
    try:
        wrapper = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # Not JSON — treat as a plain string
        return value

    if not isinstance(wrapper, dict):
        return value

    type_url = wrapper.get("typeUrl", "")
    hex_value = wrapper.get("value", "")

    if not hex_value:
        logger.warning(f"decode_attribute_value: empty hex payload for typeUrl={type_url!r}")
        return value

    try:
        raw_bytes = binascii.unhexlify(hex_value)
    except (binascii.Error, ValueError) as e:
        logger.warning(f"decode_attribute_value: hex decode failed ({e}) for typeUrl={type_url!r}")
        return value

    if "google.protobuf.Struct" in type_url:
        try:
            proto = ProtoStruct()
            proto.ParseFromString(raw_bytes)
            return MessageToDict(proto)
        except Exception as e:
            logger.warning(f"decode_attribute_value: Struct parse failed ({e})")
            return value

    if "google.protobuf.StringValue" in type_url:
        sv = StringValue()
        try:
            sv.ParseFromString(raw_bytes)
            return sv.value.strip()
        except Exception as e:
            logger.warning(f"decode_attribute_value: StringValue parse failed ({e})")
            return value

    # Unknown typeUrl — return the hex string as-is so no data is lost
    logger.warning(f"decode_attribute_value: unhandled typeUrl={type_url!r}, returning value as-is")
    return value


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

    result = _handle_response(response, "get_entity_attribute")

    if isinstance(result, dict) and "value" in result:
        result["value"] = decode_attribute_value(result["value"])
    return result


# def _process_attribute_value(val: Any) -> Any:
#     """Helper to decode simple strings or tabular data in attributes."""
#     if isinstance(val, str):
#         return decode_protobuf_name(val)
#     elif isinstance(val, list):
#         for row in val:
#             if isinstance(row, dict):
#                 for k, v in row.items():
#                     if isinstance(v, str):
#                         row[k] = decode_protobuf_name(v)
#     return val


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
    
    result = _handle_response(response, "get_entity_relations")
    # Decode names in relation objects (returned as a list)
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and "name" in item:
                item["name"] = decode_protobuf_name(item["name"])
    return result

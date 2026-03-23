"""
Utility helpers for the OpenGIN MCP client.

  - Protobuf decoding: decode_protobuf_name, decode_attribute_value
  - HTTP response handling: handle_response, _safe_json
"""

import json
import binascii
import logging
from typing import Any

import httpx
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.struct_pb2 import Struct as ProtoStruct
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)

def decode_protobuf_name(name: str) -> str:
    """
    Decode a protobuf-wrapped entity name returned by the OpenGIN API.

    The API encodes names as a JSON string:
        {"typeUrl": "...", "value": "<hex>"}
    where the hex bytes are a serialised google.protobuf.StringValue.

    Falls back to raw UTF-8 decoding, and then to returning the original
    string unchanged so no data is lost.
    """
    try:
        data = json.loads(name)
        hex_value = data.get("value")
        if not hex_value:
            logger.warning(f"decode_protobuf_name: empty hex payload: {name}")
            return name

        decoded_bytes = binascii.unhexlify(hex_value)

        sv = StringValue()
        try:
            sv.ParseFromString(decoded_bytes)
            if sv.value.strip() == "":
                return decoded_bytes.decode("utf-8", errors="ignore").strip()
            return sv.value.strip()
        except Exception:
            # Fallback: treat raw bytes as UTF-8 and strip non-printable chars
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
            cleaned = "".join(ch for ch in decoded_str if ch.isprintable())
            return cleaned.strip()
    except Exception as e:
        logger.warning(f"decode_protobuf_name: failed ({e}): {name}")
        return name


def decode_attribute_value(value: Any) -> Any:
    """
    Decode an attribute value returned by the OpenGIN API.

    The API wraps attribute values as a JSON string with shape:
        {"typeUrl": "type.googleapis.com/...", "value": "<hex>"}

    Supported typeUrls:
      - google.protobuf.Struct       → plain Python dict
      - google.protobuf.StringValue  → plain Python str

    Falls back to returning the raw value string on any error so no data
    is lost.
    """
    if not isinstance(value, str):
        return value

    try:
        wrapper = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value  # plain string, not a protobuf wrapper

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

    # Unknown typeUrl — return as-is to avoid data loss
    logger.warning(f"decode_attribute_value: unhandled typeUrl={type_url!r}, returning value as-is")
    return value

def handle_response(response: httpx.Response, context: str) -> Any:
    """
    Raise a descriptive ValueError for non-2xx responses,
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

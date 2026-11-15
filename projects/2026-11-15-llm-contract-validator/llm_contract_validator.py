#!/usr/bin/env python3
"""Validate JSON-shaped LLM output against a small, portable contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def type_matches(value: Any, expected: str) -> bool:
    if expected not in TYPE_MAP:
        raise ValueError(f"Unsupported type in contract: {expected}")
    if expected in {"number", "integer"} and isinstance(value, bool):
        return False
    return isinstance(value, TYPE_MAP[expected])


def validate(payload: Any, contract: dict[str, Any]) -> list[dict[str, str]]:
    """Return deterministic contract violations for a JSON object."""
    if not isinstance(payload, dict):
        return [{"path": "$", "code": "type", "message": "Expected a JSON object."}]

    required = contract.get("required", {})
    if not isinstance(required, dict):
        raise ValueError("Contract field 'required' must be an object.")

    errors: list[dict[str, str]] = []
    for field, expected in required.items():
        path = f"$.{field}"
        if field not in payload:
            errors.append({"path": path, "code": "missing", "message": "Required field is missing."})
        elif not isinstance(expected, str):
            raise ValueError(f"Expected type for '{field}' must be a string.")
        elif not type_matches(payload[field], expected):
            errors.append({"path": path, "code": "type", "message": f"Expected {expected}, got {type(payload[field]).__name__}."})

    if contract.get("allow_extra", True) is False:
        for field in sorted(set(payload) - set(required)):
            errors.append({"path": f"$.{field}", "code": "extra", "message": "Field is not allowed by the contract."})

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="JSON file produced by the LLM")
    parser.add_argument("contract", type=Path, help="JSON contract file")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        errors = validate(payload, contract)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))

    report = {"valid": not errors, "error_count": len(errors), "errors": errors}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compare baseline and candidate LLM evaluation results stored as JSONL."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{number}: {error.msg}") from error
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{number}: each row must be a JSON object")
            rows.append(row)
    return rows


def index_results(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("Every row requires a non-empty string 'id'.")
        if not isinstance(row.get("passed"), bool):
            raise ValueError(f"Case '{case_id}' requires boolean 'passed'.")
        if case_id in indexed:
            raise ValueError(f"Duplicate case id: {case_id}")
        indexed[case_id] = row
    return indexed


def pass_rate(rows: dict[str, dict[str, Any]]) -> float:
    return round(sum(row["passed"] for row in rows.values()) / len(rows), 4) if rows else 0.0


def compare(baseline_rows: list[dict[str, Any]], candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = index_results(baseline_rows)
    candidate = index_results(candidate_rows)
    shared = sorted(set(baseline) & set(candidate))
    regressions = [case_id for case_id in shared if baseline[case_id]["passed"] and not candidate[case_id]["passed"]]
    improvements = [case_id for case_id in shared if not baseline[case_id]["passed"] and candidate[case_id]["passed"]]

    latency_deltas = [
        float(candidate[case_id]["latency_ms"]) - float(baseline[case_id]["latency_ms"])
        for case_id in shared
        if isinstance(baseline[case_id].get("latency_ms"), (int, float))
        and isinstance(candidate[case_id].get("latency_ms"), (int, float))
    ]

    return {
        "baseline_cases": len(baseline),
        "candidate_cases": len(candidate),
        "shared_cases": len(shared),
        "baseline_pass_rate": pass_rate(baseline),
        "candidate_pass_rate": pass_rate(candidate),
        "regressions": regressions,
        "improvements": improvements,
        "new_cases": sorted(set(candidate) - set(baseline)),
        "removed_cases": sorted(set(baseline) - set(candidate)),
        "median_latency_delta_ms": round(statistics.median(latency_deltas), 2) if latency_deltas else None,
        "release_recommended": not regressions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="Baseline JSONL results")
    parser.add_argument("candidate", type=Path, help="Candidate JSONL results")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    try:
        report = compare(read_jsonl(args.baseline), read_jsonl(args.candidate))
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["release_recommended"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

# LLM Eval Diff

A dependency-free CLI that compares baseline and candidate LLM evaluation results. It highlights regressions, improvements, pass-rate changes, new or removed cases, and median latency movement—useful for release gates and model/prompt upgrades.

## Requirements

- Python 3.10+
- No external packages

## Input format

Provide one JSON object per line for both the baseline and candidate files:

```json
{"id": "support-refund", "passed": true, "latency_ms": 830}
{"id": "sql-safety", "passed": false, "latency_ms": 440}
```

Every record requires:

- `id`: a unique case identifier
- `passed`: a boolean evaluation result

`latency_ms` is optional. When present in both versions of a case, it contributes to the median latency delta.

## Usage

```bash
cd projects/2026-11-23-llm-eval-diff
python3 llm_eval_diff.py baseline.jsonl candidate.jsonl --output report.json
```

The report lists regressions, improvements, case-set changes, pass rates, and a `release_recommended` flag. The command exits with status 1 when a regression is found, so it can be used directly in CI.

## Verification

```bash
cd projects/2026-11-23-llm-eval-diff
python3 -m unittest -v
```

The test suite covers regressions, improvements, release gating, latency calculations, duplicate IDs, and invalid rows.

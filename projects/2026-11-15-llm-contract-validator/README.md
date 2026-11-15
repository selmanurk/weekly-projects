# LLM Contract Validator

A dependency-free Python CLI for checking structured LLM output against a small JSON contract. Use it as a guardrail in scripts, CI jobs, or API workflows where an LLM response must contain specific fields and types.

The contract supports:

- Required top-level fields
- Primitive types: `string`, `number`, `integer`, `boolean`, `array`, and `object`
- Optional rejection of unexpected fields

## Requirements

- Python 3.10+
- No external packages

## Usage

Create a payload file:

```json
{
  "summary": "Deployment is ready",
  "confidence": 0.92,
  "tags": ["release", "backend"]
}
```

Create a contract file:

```json
{
  "required": {
    "summary": "string",
    "confidence": "number",
    "tags": "array"
  },
  "allow_extra": false
}
```

Then validate:

```bash
cd projects/2026-11-15-llm-contract-validator
python3 llm_contract_validator.py payload.json contract.json --output report.json
```

The report includes `valid`, an error count, and deterministic field-level violations. The command exits with status 0 for valid output and 1 for invalid output, which makes it suitable for CI and automation.

## Verification

```bash
cd projects/2026-11-15-llm-contract-validator
python3 -m unittest -v
```

The tests cover valid payloads, missing fields, invalid types, extra fields, and non-object JSON input.

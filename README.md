# Regression Mini Fixture

This project is a small regression fixture for BrainAFK.

It is intentionally designed to contain a mix of:

- insecure routes that should continue to be detected
- safer control routes that should avoid false positives

The code is meant to be easy for static analysis to read. It does not need to
be deployed as a production service.

## Intended Dangerous Cases

- Path traversal via `/download`
- Command injection via `/admin/run`
- Unsafe eval via `/debug/eval`
- Server-side template injection via `/preview`
- SSRF via `/fetch`
- Weak authorization via `/admin/users/delete`

## Intended Safe Controls

- Safe file download via `/safe/download`
- Safe subprocess invocation via `/safe/run`
- Safe admin deletion via `/safe/admin/users/delete`

## Layout

- `app.py`: route registration and entrypoints
- `handlers/`: request handlers
- `services/`: unsafe business logic
- `safe/`: safer comparison implementations
- `data/`: local fixture data

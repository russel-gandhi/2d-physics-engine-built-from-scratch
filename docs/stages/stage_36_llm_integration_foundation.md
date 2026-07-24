# Stage 36 — LLM Integration Foundation

**Phase 8. Depends on:** Stage 28 (dashboard backend).

## Goal

One shared, safe, well-tested client for talking to the Gemini API — Stage 37 and 38 both build on this rather than each rolling their own API handling.

## What to build

`web/llm_client.py`
- Loads `GEMINI_API_KEY` from the environment (via `.env`, using `python-dotenv` or similar — don't hand-parse env files). If the key is missing, raise a clear error at startup with instructions, don't silently disable LLM features.
- `generate_structured(prompt, schema) -> dict`: calls Gemini asking for JSON matching a given schema, parses the response, and validates it actually matches the expected shape (keys present, values in expected ranges). If the model returns malformed JSON or an out-of-range value, retry once with a stricter prompt; if it still fails, raise a clear error rather than silently substituting a default.
- `generate_text(prompt, max_tokens) -> str`: a simpler call for free-text output (used by Stage 38's commentary).
- Basic error handling for network failures/timeouts/rate limits — surface these as clear errors to the caller, don't swallow them.

`.env.example` (committed) — a placeholder showing the expected variable name, e.g. `GEMINI_API_KEY=your-key-here`.
`.gitignore` — add `.env` so a real key is never committed.

## Definition of Done

- [ ] With a real key set in `.env`, `generate_structured` against a simple test schema returns real, valid parsed JSON from an actual API call — paste the real request/response, not a description
- [ ] Deliberately unsetting the key and running the app produces a clear startup error naming the missing variable, not a silent fallback or a crash with an unrelated traceback
- [ ] Deliberately sending a schema the model is likely to get wrong (or mocking a malformed response in a test) exercises the retry-then-fail path and produces a clear error, not a hang or a wrong-shaped object passed on to the caller
- [ ] `.env` is confirmed absent from `git status`/`.gitignore` coverage — verify this directly, don't assume

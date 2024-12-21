PHONY: run

run:
	uv run uvicorn src.main:app --port 8000

host:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8080

test-config:
	uv run src/config.py
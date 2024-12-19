PHONY: run

run:
	uv run uvicorn src.main:app --port 8000

# Makefile — developer rituals

env:
	cp .env.template .env

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

test:
	pytest -q

.PHONY: test-local
test-local:
	# Run tests with .env.local loaded but exclude keys that trigger
	# import-time guards (OPENAI_API_KEY, LOCAL_DEV_MODE). This mirrors
	# the command used during test stabilization.
	@unset OPENAI_API_KEY TEST_ACCESS_TOKEN LOCAL_DEV_MODE || true
	@env $(grep -v '^#' .env.local | grep '=' | grep -v '^OPENAI_API_KEY=' | grep -v '^LOCAL_DEV_MODE=' | awk -F= '{if($$2!="") printf "%s=%s ", $$1, $$2}') pytest -q

enrich:
	python3 enrich_runner.py

logs:
	tail -n 20 logs/enrich.log

format:
	black . && ruff check . --fix

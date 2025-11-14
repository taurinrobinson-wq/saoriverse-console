# Makefile — developer rituals

env:
	cp .env.template .env

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

test:
	pytest -q

enrich:
	python3 enrich_runner.py

logs:
	tail -n 20 logs/enrich.log

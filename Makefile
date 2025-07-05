.PHONY: install run cli lint clean

install:
	pip install -e .

run:
	python run_agent.py

cli:
	python cli.py

lint:
	ruff . && black . --check

format:
	black .

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf __pycache__ .pytest_cache dist build *.egg-info

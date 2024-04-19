.SILENT:

install:
	python3 -m venv venv; \
	source ./venv/bin/activate; \
	pip install -r requirements.txt;
	pip install -e .

clean:
	rm -rf venv; \
	find . -type f -name *.pyc -delete; \
	find . -type d -name __pycache__ -delete;

format:
	black logreef
	black tests
	black scripts

test:
	docker compose run --build --rm test pytest -s

server:
	docker compose up -d --build

deploy:
	./scripts/deploy.sh
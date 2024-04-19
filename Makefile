.SILENT:

install:
	python3 -m venv venv; \
	source ./venv/bin/activate; \
	pip install -r requirements.txt;
	pip install -e .

server:
	source ./venv/bin/activate; \
	uvicorn logreef.main:app --reload

clean:
	rm -rf venv; \
	find . -type f -name *.pyc -delete; \
	find . -type d -name __pycache__ -delete;

format:
	black logreef
	black tests
	black scripts

build: 
	docker build -t logreef-api .

run:
	docker run -it -p 80:80 logreef-api

test:
	docker compose run --build --rm test pytest -s

deploy:
	./scripts/deploy.sh

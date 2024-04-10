.SILENT:

install:
	python3 -m venv venv; \
	source ./venv/bin/activate; \
	pip install -r requirements.txt;

server:
	source ./venv/bin/activate; \
	uvicorn api.main:app --reload

clean:
	rm -rf venv; \
	find . -type f -name *.pyc -delete; \
	find . -type d -name __pycache__ -delete;

format:
	black populate.py
	black api
	black tests

build: 
	docker build -t aqualog-api .

run:
	docker run -d -p 80:80 aqualog-api

test:
	pytest -s

deploy:
	./scripts/deploy.sh

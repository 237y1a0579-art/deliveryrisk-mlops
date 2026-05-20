.PHONY: setup data train api test lint dvc frontend promptfoo

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

data:
	python -m pipelines.ingest
	python -m pipelines.validate
	python -m pipelines.features

train:
	python -m pipelines.train

dvc:
	dvc repro

api:
	uvicorn services.api.app.main:app --reload --port 8000

frontend:
	cd services/frontend && npm run dev

test:
	pytest

lint:
	ruff check .

promptfoo:
	cd promptfoo && npx promptfoo@latest eval -c promptfooconfig.yaml


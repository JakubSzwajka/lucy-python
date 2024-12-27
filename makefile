
format: 
	ruff format .

serve:
	python src/main.py 

plot:
	python src/plot.py

compile:
	pip-compile requirements.in

install:
	pip install pip-tools
	pip-sync requirements.txt

run-qdrant-local: 
	docker run -p 6333:6333 -p 6334:6334 \
		-v ./qdrant_storage:/qdrant/storage:z \
		qdrant/qdrant
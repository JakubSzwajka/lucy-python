
format: 
	ruff format .

chat: 
	python src/cli/app.py

serve:
	python src/main.py


compile:
	pip-compile requirements.in

install:
	pip install -r requirements.txt

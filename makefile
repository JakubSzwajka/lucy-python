
format: 
	ruff format .

chat: 
	python src/main_cli.py

serve:
	python src/main.py 


compile:
	pip-compile requirements.in

install:
	pip-sync requirements.txt

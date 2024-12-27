FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

# Expose the port and set the entrypoint
EXPOSE 8000

CMD ["python", "src/main.py"]

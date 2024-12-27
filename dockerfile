FROM python:3.12-slim

WORKDIR /app

# Copy in the requirements files
COPY requirements.in .
COPY requirements.txt .

# Install pip-tools (in case you want to re-compile) and all dependencies
RUN pip install --upgrade pip pip-tools &&
    pip install -r requirements.txt

# Copy the rest of the code into the container
COPY . .

# Expose the port and set the entrypoint
EXPOSE 8000

CMD ["python", "src/main.py"]

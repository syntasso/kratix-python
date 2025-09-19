FROM python:3.12-slim

RUN apt-get update && apt-get install -y git

RUN python -m pip install git+https://github.com/syntasso/kratix-python.git

WORKDIR /app
COPY scripts/pipeline.py /app/pipeline.py

ENTRYPOINT ["python", "-u", "/app/pipeline.py"]
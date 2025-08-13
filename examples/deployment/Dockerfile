FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN pip install --no-cache-dir kubernetes

RUN python -m pip install git+https://github.com/syntasso/kratix-python.git

# Put /app on PYTHONPATH so kratix_sdk is importable
ENV PYTHONPATH=/app

COPY examples/deployment /app/examples/deployment

WORKDIR /app/examples/deployment

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["echo Set command to promise-configure or resource-configure"]

FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir kubernetes

COPY kratix_sdk /app/kratix_sdk

# Put /app on PYTHONPATH so kratix_sdk is importable
ENV PYTHONPATH=/app

COPY example/deployment /app/example/deployment

WORKDIR /app/example/deployment

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["echo Set command to promise-configure or resource-configure"]

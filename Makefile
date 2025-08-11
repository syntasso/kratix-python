PYTHON := python # or python3, depending on your environment
PIP := $(PYTHON) -m pip

.PHONY: test lint clean

install: # install dependencies for running tests and linting
	$(PIP) install --upgrade pip
	$(PIP) install ruff pytest pyyaml

test:
	pytest

lint:
	ruff check kratix_sdk tests

fmt:
	ruff format kratix_sdk tests

build-and-load-configure-image:
	docker buildx build --builder kratix-image-builder --load --platform linux/arm64 \
	-t ghcr.io/syntasso/example-deployment-configure:v0.0.1 -f example/deployment/Dockerfile .
	kind load docker-image ghcr.io/syntasso/example-deployment-configure:v0.0.1 -n platform

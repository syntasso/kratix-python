UV_PYTHON ?= 3.12

.PHONY: test lint fmt clean install

install: # install dependencies for running tests and linting
	uv sync --extra dev

test:
	uv run --isolated --with-editable '.[dev]' pytest

lint: install
	uv run ruff check kratix_sdk tests
	uv run ruff format --check kratix_sdk tests

fmt: install
	uv run ruff format kratix_sdk tests

generate-docs:
	uv run pdoc src/kratix_sdk -o docs

build-and-load-configure-image:
	docker buildx build --builder kratix-image-builder --load --platform linux/arm64 \
	-t ghcr.io/syntasso/example-deployment-configure:v0.0.1 -f examples/deployment/Dockerfile .
	kind load docker-image ghcr.io/syntasso/example-deployment-configure:v0.0.1 -n platform

build-and-load-system-test-image:
	docker buildx build --builder kratix-image-builder --load --platform linux/arm64 \
	-t ghcr.io/syntasso/kratix-python/sdk-test:v1.0.0 -f system/assets/workflow/Dockerfile .
	kind load docker-image ghcr.io/syntasso/kratix-python/sdk-test:v1.0.0 -n platform

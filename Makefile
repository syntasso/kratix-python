.PHONY: build help install test lint fmt generate-docs build-and-load-configure image build-and-load-system-test-image

help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;34m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

install: # install dependencies for running tests and linting
	uv python install

dev: install # Install development/release dependencies
	uv sync --extra dev

build: install # build package
	uv build

test: install dev # run tests
	uv run --isolated --with-editable '.[dev]' pytest

lint: install dev # run linting checks
	uv run ruff check kratix_sdk tests
	uv run ruff format --check kratix_sdk tests

fmt: install dev # run code formatter
	uv run ruff format kratix_sdk tests

generate-docs: install dev # create API documentation
	uv run pdoc src/kratix_sdk -o docs

build-and-load-configure-image: # build example docker image and load it into kind
	docker buildx build --builder kratix-image-builder --load --platform linux/arm64 \
	-t ghcr.io/syntasso/example-deployment-configure:v0.0.1 -f examples/deployment/Dockerfile .
	kind load docker-image ghcr.io/syntasso/example-deployment-configure:v0.0.1 -n platform

build-and-load-system-test-image: # build integration test docker image and load it into kind
	docker buildx build --builder kratix-image-builder --load --platform linux/arm64 \
	-t ghcr.io/syntasso/kratix-python/sdk-test:v1.0.0 -f system/assets/workflow/Dockerfile .
	kind load docker-image ghcr.io/syntasso/kratix-python/sdk-test:v1.0.0 -n platform

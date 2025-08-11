# kratix-python

This SDK was implemented in line with the [Kratix SDK Contract](https://github.com/syntasso/kratix/blob/main/sdk/contract.go).

## Usage & Development

Library is under `kratix_sdk`. Examples of Promises using this library can be found under `examples`.

* `make test` runs all tests under `tests/`

* `make fmt` code formatting using `ruff`

* `make lint` linting using `ruff`

* `make build-and-load-configure-image` build and load the image used for example/deployment/promise.yaml to your local kind cluster
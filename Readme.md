# kratix-python

You can read library document [here](https://syntasso.github.io/kratix-python).

## Installation

```bash
# From PyPI (preferred once published)
pip install kratix-sdk

# From the main branch
pip install git+https://github.com/syntasso/kratix-python.git

# Editable install for local development
pip install -e .
```

## Usage

```python
import kratix_sdk as ks
import yaml

# Initialize the sdk
sdk = ks.KratixSDK()
resource = sdk.read_resource_input()

# Read from resource input
name = resource.get_value("spec.key")

# Write workload documents to OUTPUT_DIR
manifest = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": name, "labels": {"app": name}},
    "spec": {
        "replicas": 1,
        "selector": {"matchLabels": {"app": name}},
        "template": {
            "metadata": {"labels": {"app": name}},
            "spec": {
                "containers": [
                    {"name": name, "image": "busybox"}
                ]
            },
        },
    },
}
data = yaml.safe_dump(manifest).encode("utf-8")
sdk.write_output("deployment.yaml", data)

# Publish status during workflow run
status = ks.Status()
status.set("phase", "updates-from-mid-stage")
sdk.publish_status(resource, status)

# Set status
status = ks.Status()
status.set("message", f"created deployment {key}")
sdk.write_status(status)

# Write destination selectors for dynamic scheduling
selectors: List[ks.DestinationSelector] = [
    ks.DestinationSelector(match_labels={"environment": "test"})
]
sdk.write_destination_selectors(selectors)
```

## Development

Library is under `kratix_sdk`. Examples of Promises using this library can be found under `examples`.

* `make install` installs all dependencies

* `make test` runs all tests under `tests/`

* `make fmt` code formatting using `ruff`

* `make lint` linting using `ruff`

See `RELEASING.md` for the tested release workflow when publishing to TestPyPI/PyPI.

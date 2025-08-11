# examples/handlers.py
from __future__ import annotations

import sys
from typing import List

import yaml
import kratix_sdk as ks  # your package


def promise_configure() -> int:
    """Read the Promise and print its name (stdout)."""
    sdk = ks.KratixSDK()
    promise = sdk.read_promise_input()
    name = promise.get_name()
    print(name)  # Kratix captures stdout as pipeline output
    return 0


def _deployment_manifest(name: str) -> dict:
    """Minimal valid Deployment manifest named after `name`."""
    return {
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
                        {"name": name, "image": "nginx:1.25", "ports": [{"containerPort": 80}]}
                    ]
                },
            },
        },
    }


def resource_configure() -> int:
    sdk = ks.KratixSDK()
    resource = sdk.read_resource_input()

    key = resource.get_value("spec.key")
    if not key or not isinstance(key, str):
        raise SystemExit("spec.key is required and must be a non-empty string")

    # 1) Write a Deployment manifest to OUTPUT_DIR
    manifest = _deployment_manifest(key)
    data = yaml.safe_dump(manifest).encode("utf-8")
    sdk.write_output("deployment.yaml", data)

    # 2) set the status
    status = ks.Status()
    status.set("message", f"created deployment {key}")
    sdk.write_status(status)

    # 3) Destination selectors
    selectors: List[ks.DestinationSelector] = [
        ks.DestinationSelector(match_labels={"environment": "test"})
    ]
    sdk.write_destination_selectors(selectors)

    return 0


def main() -> int:
    # Dispatch by argv[1]
    if len(sys.argv) < 2:
        print("usage: handlers.py [promise-configure|resource-configure]", file=sys.stderr)
        return 2

    cmd = sys.argv[1]
    if cmd == "promise-configure":
        return promise_configure()
    if cmd == "resource-configure":
        return resource_configure()

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import List
from kubernetes import client as k8s_client, config as k8s_config
from .resource import Resource
from .types import DestinationSelector
from .status import Status
from .promise import Promise

INPUT_DIR = Path("/kratix/input")
OUTPUT_DIR = Path("/kratix/output")
METADATA_DIR = Path("/kratix/metadata")


def get_input_dir() -> Path:
    return INPUT_DIR


def get_output_dir() -> Path:
    return OUTPUT_DIR


def get_metadata_dir() -> Path:
    return METADATA_DIR


def set_input_dir(path: Path | str) -> None:
    global INPUT_DIR
    INPUT_DIR = Path(path)


def set_output_dir(path: Path | str) -> None:
    global OUTPUT_DIR
    OUTPUT_DIR = Path(path)


def set_metadata_dir(path: Path | str) -> None:
    global METADATA_DIR
    METADATA_DIR = Path(path)


class KratixSDK:
    def read_resource_input(self) -> Resource:
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Resource(data)

    def read_promise_input(self) -> Promise:
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Promise(data)

    def read_status(self) -> Status:
        path = METADATA_DIR / "status.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Status(data)

    def read_destination_selectors(self) -> List[DestinationSelector]:
        path = METADATA_DIR / "destination-selectors.yaml"
        with path.open() as f:
            raw = yaml.safe_load(f) or []
        selectors = [
            DestinationSelector(
                directory=item.get("directory", ""),
                match_labels=item.get("matchLabels", {}) or {},
            )
            for item in raw
        ]
        return selectors

    def write_output(self, relative_path: str, content: bytes) -> None:
        dest = OUTPUT_DIR / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            f.write(content)

    def write_status(self, status: Status) -> None:
        path = METADATA_DIR / "status.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(status.to_dict(), f)

    def write_destination_selectors(self, selectors: List[DestinationSelector]) -> None:
        path = METADATA_DIR / "destination-selectors.yaml"
        data = []
        for s in selectors:
            data.append({
                "directory": s.directory or "",   # directory is optional
                "matchLabels": s.match_labels or {},
            })
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(data, f)

    def workflow_action(self) -> str:
        return os.getenv("KRATIX_WORKFLOW_ACTION", "")

    def workflow_type(self) -> str:
        return os.getenv("KRATIX_WORKFLOW_TYPE", "")

    def promise_name(self) -> str:
        return os.getenv("KRATIX_PROMISE_NAME", "")

    def pipeline_name(self) -> str:
        return os.getenv("KRATIX_PIPELINE_NAME", "")

    def publish_status(self, resource: Resource, status: Status) -> None:
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()

        gvk = resource.get_group_version_kind()
        plural = os.getenv("KRATIX_CRD_PLURAL")
        if not plural:
            raise RuntimeError("KRATIX_CRD_PLURAL environment variable is not set")

        namespace = resource.get_namespace()
        name = resource.get_name()
        body = {"status": status.to_dict()}

        api = k8s_client.CustomObjectsApi()
        api.patch_namespaced_custom_object_status(
            group=gvk.group,
            version=gvk.version,
            namespace=namespace,
            plural=plural,
            name=name,
            body=body,
        )

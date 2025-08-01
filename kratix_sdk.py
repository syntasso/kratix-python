from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

INPUT_DIR = Path("/kratix/input")
OUTPUT_DIR = Path("/kratix/output")


def _get_by_path(data: Dict[str, Any], path: str) -> Any:
    current = data
    if not path:
        return current
    for key in path.split("."):
        if not isinstance(current, dict):
            raise KeyError(f"Cannot descend into non-dict at {key}")
        current = current[key]
    return current


def _set_by_path(data: Dict[str, Any], path: str, value: Any) -> None:
    current = data
    keys = path.split(".")
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def _remove_by_path(data: Dict[str, Any], path: str) -> bool:
    current = data
    keys = path.split(".")
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            return False
        current = current[key]
    return current.pop(keys[-1], None) is not None


@dataclass
class GroupVersionKind:
    group: str
    version: str
    kind: str


@dataclass
class DestinationSelector:
    directory: str
    match_labels: Dict[str, Any] = field(default_factory=dict)


class Status:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data: Dict[str, Any] = data or {}

    def get(self, path: str) -> Any:
        return _get_by_path(self.data, path)

    def set(self, path: str, value: Any) -> None:
        _set_by_path(self.data, path, value)

    def remove(self, path: str) -> bool:
        return _remove_by_path(self.data, path)

    def to_dict(self) -> Dict[str, Any]:
        return self.data


class Resource:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def get_value(self, path: str) -> Any:
        return _get_by_path(self.data, path)

    def get_status(self, path: str = "") -> Status:
        status_data = self.data.get("status", {})
        if path:
            value = _get_by_path(status_data, path)
            return Status(value if isinstance(value, dict) else {"value": value})
        return Status(status_data)

    def get_name(self) -> str:
        return self.data.get("metadata", {}).get("name", "")

    def get_namespace(self) -> str:
        return self.data.get("metadata", {}).get("namespace", "")

    def get_group_version_kind(self) -> GroupVersionKind:
        api_version = self.data.get("apiVersion", "")
        if "/" in api_version:
            group, version = api_version.split("/", 1)
        else:
            group, version = "", api_version
        kind = self.data.get("kind", "")
        return GroupVersionKind(group=group, version=version, kind=kind)

    def get_labels(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("labels", {})

    def get_annotations(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("annotations", {})

    def update_status(self, status: Status) -> None:
        self.data["status"] = status.to_dict()


# Promise has no specific behaviour; reuse Resource structure.
Promise = Resource


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

    def read_destination_selectors(self) -> List[DestinationSelector]:
        path = INPUT_DIR / "destination_selectors.yaml"
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
        path = OUTPUT_DIR / "status.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(status.to_dict(), f)

    def write_destination_selectors(
        self, selectors: List[DestinationSelector]
    ) -> None:
        path = OUTPUT_DIR / "destination_selectors.yaml"
        data = [
            {"directory": s.directory, "matchLabels": s.match_labels}
            for s in selectors
        ]
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
        resource.update_status(status)

    def read_status(self) -> Status:
        path = OUTPUT_DIR / "status.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Status(data)


from __future__ import annotations
from typing import Any, Dict
from .utils import _get_by_path
from .status import Status
from .types import GroupVersionKind


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

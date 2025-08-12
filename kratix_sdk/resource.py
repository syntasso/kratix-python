from typing import Any, Dict
from .utils import _get_by_path
from .status import Status
from .types import GroupVersionKind


class Resource:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def get_value(self, path: str) -> Any:
        """Get a value from the resource request by path."""
        return _get_by_path(self.data, path)

    def get_status(self, path: str = "") -> Status:
        """Get the status of the resource by path.
        If path is empty, return the entire status.
        If path is provided, return the value at that path."""
        status_data = self.data.get("status", {})
        if path:
            value = _get_by_path(status_data, path)
            return Status(value if isinstance(value, dict) else {"value": value})
        return Status(status_data)

    def get_name(self) -> str:
        """Get the name of the resource."""
        return self.data.get("metadata", {}).get("name", "")

    def get_namespace(self) -> str:
        """Get the namespace of the resource."""
        return self.data.get("metadata", {}).get("namespace", "")

    def get_group_version_kind(self) -> GroupVersionKind:
        """Get the GroupVersionKind of the resource."""
        api_version = self.data.get("apiVersion", "")
        if "/" in api_version:
            group, version = api_version.split("/", 1)
        else:
            group, version = "", api_version
        kind = self.data.get("kind", "")
        return GroupVersionKind(group=group, version=version, kind=kind)

    def get_labels(self) -> Dict[str, str]:
        """Get the labels of the resource."""
        return self.data.get("metadata", {}).get("labels", {})

    def get_annotations(self) -> Dict[str, str]:
        """Get the annotations of the resource."""
        return self.data.get("metadata", {}).get("annotations", {})

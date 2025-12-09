from typing import Any

from .status import Status
from .types import GroupVersionKind
from .utils import _get_by_path


class Resource:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_value(self, path: str, **kwargs) -> Any:
        """Get a value from the resource request by path.
        Args:
            path (str): The path to the value in the resource data.

        KWargs:
            default: The default value to return if the path is not found.

        Raises:
            KeyError: If the path is not found and no default is provided.

        Returns:
            Any: The value at the specified path in the resource data.
        """
        return _get_by_path(self.data, path, **kwargs)

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

    def get_labels(self) -> dict[str, str]:
        """Get the labels of the resource."""
        return self.data.get("metadata", {}).get("labels", {})

    def get_annotations(self) -> dict[str, str]:
        """Get the annotations of the resource."""
        return self.data.get("metadata", {}).get("annotations", {})

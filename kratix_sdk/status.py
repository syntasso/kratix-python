from typing import Any

from .utils import _get_by_path, _remove_by_path, _set_by_path


class Status:
    def __init__(self, data: dict[str, Any] | None = None):
        self.data: dict[str, Any] = data or {}

    def get(self, path: str) -> Any:
        """Retrieves the value at the specified path in Status."""
        return _get_by_path(self.data, path)

    def set(self, path: str, value: Any) -> None:
        """Sets the value at the specified path in Status."""
        _set_by_path(self.data, path, value)

    def remove(self, path: str) -> None:
        """Removes the value at the specified path in Status.
        If the path does not exist, it retursn an error."""
        _remove_by_path(self.data, path)

    def to_dict(self) -> dict[str, Any]:
        return self.data

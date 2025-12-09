from typing import Any


class Promise:
    def __init__(self, data: dict[str, Any] | None = None):
        self.data: dict[str, Any] = data or {}

    def get_name(self) -> str:
        """Get the name of the promise."""
        return self.data.get("metadata", {}).get("name", "")

    def get_labels(self) -> dict[str, str]:
        """Get the labels of the promise."""
        return self.data.get("metadata", {}).get("labels", {}) or {}

    def get_annotations(self) -> dict[str, str]:
        """Get the annotations of the promise."""
        return self.data.get("metadata", {}).get("annotations", {}) or {}

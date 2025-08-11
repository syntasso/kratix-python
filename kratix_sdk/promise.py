from typing import Any, Dict, Optional


class Promise:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data: Dict[str, Any] = data or {}

    def get_name(self) -> str:
        return self.data.get("metadata", {}).get("name", "")

    def get_labels(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("labels", {}) or {}

    def get_annotations(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("annotations", {}) or {}

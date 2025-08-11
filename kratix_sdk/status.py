from __future__ import annotations

from typing import Any, Dict, Optional
from .utils import _get_by_path, _set_by_path, _remove_by_path

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
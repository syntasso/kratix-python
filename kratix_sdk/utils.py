from typing import Any, Dict


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

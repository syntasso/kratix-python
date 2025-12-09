from typing import Any


def _get_by_path(data: dict[str, Any], path: str, **kwargs) -> Any:
    has_default_key = "default" in kwargs

    current = data
    if not path:
        return current
    for key in path.split("."):
        if not isinstance(current, dict):
            raise KeyError(f"Cannot descend into non-dict at {key}")
        if key not in current:
            if has_default_key:
                return kwargs["default"]
            raise KeyError(f"Missing key in path: '{key}'")
        current = current[key]
    return current


def _set_by_path(data: dict[str, Any], path: str, value: Any) -> None:
    if not path:
        raise ValueError("Empty path")

    current: Any = data
    keys = path.split(".")

    for key in keys[:-1]:
        if not isinstance(current, dict):
            raise TypeError(f"Cannot descend into non-dict when setting '{key}'")
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            raise TypeError(
                f"Path '{key}' is a non-dict; cannot create child keys under it"
            )
        current = current[key]

    if not isinstance(current, dict):
        raise TypeError(f"Cannot set key on non-dict at final segment '{keys[-1]}'")

    current[keys[-1]] = value


def _remove_by_path(data: dict[str, Any], path: str) -> None:
    if not path:
        raise ValueError("Empty path")

    current: Any = data
    keys = path.split(".")

    for key in keys[:-1]:
        if not isinstance(current, dict):
            raise TypeError(f"Cannot descend into non-dict when removing '{key}'")
        if key not in current:
            raise KeyError(f"Missing key in path: '{key}'")
        current = current[key]

    if not isinstance(current, dict):
        raise TypeError(f"Cannot remove key on non-dict at final segment '{keys[-1]}'")

    last = keys[-1]
    if last not in current:
        raise KeyError(f"Key to remove not found: '{last}'")

    del current[last]

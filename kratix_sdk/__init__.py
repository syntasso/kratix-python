from importlib import metadata as importlib_metadata

from .status import Status
from .resource import Resource
from .kratix_sdk import (
    KratixSDK,
    set_input_dir,
    set_output_dir,
    get_input_dir,
    get_output_dir,
    get_metadata_dir,
    set_metadata_dir,
)
from .promise import Promise
from .types import GroupVersionKind, DestinationSelector

try:
    __version__ = importlib_metadata.version("kratix-sdk")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover - source tree fallback
    __version__ = "0.0.0"

__all__ = [
    "Status",
    "Resource",
    "Promise",
    "GroupVersionKind",
    "DestinationSelector",
    "KratixSDK",
    "set_input_dir",
    "set_output_dir",
    "get_input_dir",
    "get_output_dir",
    "get_metadata_dir",
    "set_metadata_dir",
    "__version__",
]

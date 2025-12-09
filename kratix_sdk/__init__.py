from importlib import metadata as importlib_metadata

from .kratix_sdk import (
    KratixSDK,
    get_input_dir,
    get_metadata_dir,
    get_output_dir,
    set_input_dir,
    set_metadata_dir,
    set_output_dir,
)
from .promise import Promise
from .resource import Resource
from .status import Status
from .types import DestinationSelector, GroupVersionKind

try:
    __version__ = importlib_metadata.version("kratix-sdk")
except (
    importlib_metadata.PackageNotFoundError
):  # pragma: no cover - source tree fallback
    __version__ = "0.4.1"

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

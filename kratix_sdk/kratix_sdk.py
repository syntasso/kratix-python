from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import List
from .resource import Resource
from .types import DestinationSelector
from .status import Status
from .promise import Promise

INPUT_DIR = Path("/kratix/input")
OUTPUT_DIR = Path("/kratix/output")
METADATA_DIR = Path("/kratix/metadata")

def get_input_dir() -> Path:
    return INPUT_DIR


def get_output_dir() -> Path:
    return OUTPUT_DIR


def get_metadata_dir() -> Path:
    return METADATA_DIR


def set_input_dir(path: Path | str) -> None:
    global INPUT_DIR
    INPUT_DIR = Path(path)


def set_output_dir(path: Path | str) -> None:
    global OUTPUT_DIR
    OUTPUT_DIR = Path(path)

def set_metadata_dir(path: Path | str) -> None:
    global METADATA_DIR
    METADATA_DIR = Path(path)


class KratixSDK:
    def read_resource_input(self) -> Resource:
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Resource(data)

    def read_promise_input(self) -> Promise:
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Promise(data)

    def read_destination_selectors(self) -> List[DestinationSelector]:
        path = INPUT_DIR / "destination_selectors.yaml"
        with path.open() as f:
            raw = yaml.safe_load(f) or []
        selectors = [
            DestinationSelector(
                directory=item.get("directory", ""),
                match_labels=item.get("matchLabels", {}) or {},
            )
            for item in raw
        ]
        return selectors

    def write_output(self, relative_path: str, content: bytes) -> None:
        dest = OUTPUT_DIR / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            f.write(content)

    def write_status(self, status: Status) -> None:
        path = OUTPUT_DIR / "status.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(status.to_dict(), f)

    def write_destination_selectors(self, selectors: List[DestinationSelector]) -> None:
        path = OUTPUT_DIR / "destination_selectors.yaml"
        data = [
            {"directory": s.directory, "matchLabels": s.match_labels} for s in selectors
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(data, f)

    def workflow_action(self) -> str:
        return os.getenv("KRATIX_WORKFLOW_ACTION", "")

    def workflow_type(self) -> str:
        return os.getenv("KRATIX_WORKFLOW_TYPE", "")

    def promise_name(self) -> str:
        return os.getenv("KRATIX_PROMISE_NAME", "")

    def pipeline_name(self) -> str:
        return os.getenv("KRATIX_PIPELINE_NAME", "")

    def publish_status(self, resource: Resource, status: Status) -> None:
        resource.update_status(status)

    def read_status(self) -> Status:
        path = OUTPUT_DIR / "status.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Status(data)

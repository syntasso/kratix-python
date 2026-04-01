import os
from datetime import timedelta
from pathlib import Path

import yaml
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config

from .promise import Promise
from .resource import Resource
from .status import Status
from .types import DestinationSelector

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


def timedelta_to_go_duration(td: timedelta) -> str:
    """Converts a Python timedelta to a Go duration string (e.g. "1h30m5s300ms")."""
    total_microseconds = (td.days * 86400 + td.seconds) * 1_000_000 + td.microseconds
    if total_microseconds <= 0:
        raise ValueError("duration must be positive")

    hours, remainder = divmod(total_microseconds, 3_600_000_000)
    minutes, remainder = divmod(remainder, 60_000_000)
    seconds, remainder = divmod(remainder, 1_000_000)
    milliseconds, microseconds = divmod(remainder, 1_000)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    if milliseconds:
        parts.append(f"{milliseconds}ms")
    if microseconds:
        parts.append(f"{microseconds}us")

    return "".join(parts)


class KratixSDK:
    def read_resource_input(self) -> Resource:
        """Reads the file in /kratix/input/object.yaml and returns a Resource.
        Can be used in Resource configure workflow."""
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Resource(data)

    def read_promise_input(self) -> Promise:
        """Reads the file in /kratix/input/object.yaml and returns a Promise.
        Can be used in Promise configure workflow."""
        path = INPUT_DIR / "object.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Promise(data)

    def read_status(self) -> Status:
        """Reads the file in /kratix/metadata/status.yaml and returns a Status."""
        path = METADATA_DIR / "status.yaml"
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return Status(data)

    def read_destination_selectors(self) -> list[DestinationSelector]:
        """Reads the file in /kratix/metadata/destination-selectors.yaml and
        returns a list of DestinationSelector"""
        path = METADATA_DIR / "destination-selectors.yaml"
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
        """writes the content to the specifies file at the path
        /kratix/output/relative_path."""
        dest = OUTPUT_DIR / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            f.write(content)

    def write_status(self, status: Status) -> None:
        """writes the specified status to the /kratix/metadata/status.yaml."""
        path = METADATA_DIR / "status.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(status.to_dict(), f)

    def write_destination_selectors(self, selectors: list[DestinationSelector]) -> None:
        """writes the specified Destination Selectors to the
        /kratix/metadata/destination_selectors.yaml."""
        path = METADATA_DIR / "destination-selectors.yaml"
        data = []
        for s in selectors:
            data.append(
                {
                    "directory": s.directory or "",  # directory is optional
                    "matchLabels": s.match_labels or {},
                }
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(data, f)

    def workflow_action(self) -> str:
        """Returns the value of KRATIX_WORKFLOW_ACTION environment variable."""
        return os.getenv("KRATIX_WORKFLOW_ACTION", "")

    def workflow_type(self) -> str:
        """Returns the value of KRATIX_WORKFLOW_TYPE environment variable."""
        return os.getenv("KRATIX_WORKFLOW_TYPE", "")

    def promise_name(self) -> str:
        """Returns the value of KRATIX_PROMISE_NAME environment variable."""
        return os.getenv("KRATIX_PROMISE_NAME", "")

    def pipeline_name(self) -> str:
        """Returns the value of KRATIX_PIPELINE_NAME environment variable."""
        return os.getenv("KRATIX_PIPELINE_NAME", "")

    def publish_status(self, resource: Resource, status: Status) -> None:
        """Updates the status of a Resource.
        This function uses the Kubernetes API to patch the status of a Custom Resource.
        Update is instant and will not change the /kratix/metadata/status.yaml file."""
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()

        gvk = resource.get_group_version_kind()
        plural = os.getenv("KRATIX_CRD_PLURAL")
        if not plural:
            raise RuntimeError("KRATIX_CRD_PLURAL environment variable is not set")

        namespace = resource.get_namespace()
        name = resource.get_name()

        body = {"status": status.to_dict()}
        api = k8s_client.CustomObjectsApi()
        api.api_client.set_default_header(
            "Content-Type", "application/merge-patch+json"
        )
        api.patch_namespaced_custom_object_status(
            group=gvk.group,
            version=gvk.version,
            namespace=namespace,
            plural=plural,
            name=name,
            body=body,
        )

    def is_promise_workflow(self) -> bool:
        """Returns true if the workflow is a promise workflow."""
        return self.workflow_type() == "promise"

    def is_resource_workflow(self) -> bool:
        """Returns true if the workflow is a resource workflow."""
        return self.workflow_type() == "resource"

    def is_configure_action(self) -> bool:
        """Returns true if the workflow is a configure action."""
        return self.workflow_action() == "configure"

    def is_delete_action(self) -> bool:
        """Returns true if the workflow is a delete action."""
        return self.workflow_action() == "delete"

    def write_suspend(self, message: str = "") -> None:
        """Writes workflow-control.yaml with suspend: true.

        Kratix will stop further pipeline execution and set the workflow phase to
        Suspended.

        If a message is provided, it will be surfaced in the object's status."""
        data: dict = {"suspend": True}
        if message:
            data["message"] = message
        self._write_workflow_control(data)

    def write_retry_after(self, duration: timedelta, message: str = "") -> None:
        """Writes workflow-control.yaml with retryAfter set to the given duration.

        Kratix will requeue the pipeline after the specified duration and increment
        the attempt counter in the object's status.

        If a message is provided, it will be surfaced in the object's status."""
        data: dict = {"retryAfter": timedelta_to_go_duration(duration)}
        if message:
            data["message"] = message
        self._write_workflow_control(data)

    def _write_workflow_control(self, data: dict) -> None:
        path = METADATA_DIR / "workflow-control.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(data, f)

import yaml
import pytest
from pathlib import Path

import kratix_sdk as ks


# ---------- Helpers ----------

def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(data, f)


# ---------- Unit tests for dict path helpers ----------

def test_get_by_path_happy_path():
    data = {"a": {"b": {"c": 123}}}
    assert ks._get_by_path(data, "a.b.c") == 123
    assert ks._get_by_path(data, "") == data  # empty path returns whole dict


def test_get_by_path_raises_on_non_dict():
    data = {"a": 1}
    with pytest.raises(KeyError):
        ks._get_by_path(data, "a.b")  # tries to descend into non-dict (int)


def test_set_by_path_creates_intermediates():
    data = {}
    ks._set_by_path(data, "a.b.c", 42)
    assert data == {"a": {"b": {"c": 42}}}


def test_remove_by_path_true_false():
    data = {"a": {"b": {"c": 1}}}
    assert ks._remove_by_path(data, "a.b.c") is True
    assert ks._remove_by_path(data, "a.b.c") is False  # already removed
    assert data == {"a": {"b": {}}}


# ---------- Status ----------

def test_status_get_set_remove_roundtrip():
    s = ks.Status()
    s.set("foo.bar", 7)
    assert s.get("foo.bar") == 7
    assert s.remove("foo.bar") is True
    assert s.remove("foo.bar") is False
    assert s.to_dict() == {"foo": {}}


# ---------- Resource ----------

def test_resource_basic_accessors():
    obj = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "n",
            "namespace": "ns",
            "labels": {"a": "b"},
            "annotations": {"x": "y"},
        },
        "status": {"state": "ok"},
        "spec": {"replicas": 3},
    }
    r = ks.Resource(obj)

    assert r.get_value("spec.replicas") == 3
    assert r.get_name() == "n"
    assert r.get_namespace() == "ns"
    assert r.get_labels() == {"a": "b"}
    assert r.get_annotations() == {"x": "y"}

    gvk = r.get_group_version_kind()
    assert (gvk.group, gvk.version, gvk.kind) == ("apps", "v1", "Deployment")


def test_resource_get_group_version_kind_core_group():
    obj = {"apiVersion": "v1", "kind": "ConfigMap"}
    r = ks.Resource(obj)
    gvk = r.get_group_version_kind()
    assert (gvk.group, gvk.version, gvk.kind) == ("", "v1", "ConfigMap")


def test_resource_get_status_variants():
    obj = {"status": {"nested": {"a": 1}, "leaf": 2}}
    r = ks.Resource(obj)

    # No path -> returns entire status dict
    s_all = r.get_status()
    assert s_all.to_dict() == {"nested": {"a": 1}, "leaf": 2}

    # Path to dict -> returns that dict
    s_nested = r.get_status("nested")
    assert s_nested.to_dict() == {"a": 1}

    # Path to scalar -> wraps it in {"value": <scalar>}
    s_leaf = r.get_status("leaf")
    assert s_leaf.to_dict() == {"value": 2}


def test_publish_status_updates_resource():
    r = ks.Resource({"metadata": {"name": "x"}})
    s = ks.Status({"phase": "Done"})
    ks.KratixSDK().publish_status(r, s)
    assert r.data["status"] == {"phase": "Done"}


# ---------- KratixSDK I/O ----------

def test_sdk_reads_and_writes_with_tmpdirs(tmp_path, monkeypatch):
    # Point the SDK to temp input/output
    monkeypatch.setattr(ks, "INPUT_DIR", tmp_path / "in")
    monkeypatch.setattr(ks, "OUTPUT_DIR", tmp_path / "out")
    (ks.INPUT_DIR).mkdir(parents=True)
    (ks.OUTPUT_DIR).mkdir(parents=True)

    # Prepare input object.yaml
    input_obj = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "demo"},
        "status": {"initial": True},
    }
    write_yaml(ks.INPUT_DIR / "object.yaml", input_obj)

    # read_resource_input / read_promise_input
    sdk = ks.KratixSDK()
    res = sdk.read_resource_input()
    prom = sdk.read_promise_input()  # alias of Resource
    assert isinstance(res, ks.Resource)
    assert isinstance(prom, ks.Promise)
    assert res.get_name() == "demo"
    assert prom.get_name() == "demo"

    # write_output (binary)
    sdk.write_output("artifacts/hello.txt", b"hello")
    out_file = ks.OUTPUT_DIR / "artifacts/hello.txt"
    assert out_file.read_bytes() == b"hello"

    # write_status + read_status
    status = ks.Status({"phase": "Running"})
    sdk.write_status(status)
    read_back = sdk.read_status()
    assert read_back.to_dict() == {"phase": "Running"}


def test_destination_selectors_read_write(tmp_path, monkeypatch):
    assets_dir = Path(__file__).parent / "assets"
    asset_file = assets_dir / "destination_selectors.yaml"
    assert asset_file.exists(), f"Missing test asset: {asset_file}"

    monkeypatch.setattr(ks, "INPUT_DIR", assets_dir)
    monkeypatch.setattr(ks, "OUTPUT_DIR", tmp_path / "out")
    ks.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sdk = ks.KratixSDK()

    # Read selectors from assets/destination_selectors.yaml
    selectors = sdk.read_destination_selectors()
    assert selectors[0].directory == "prod"
    assert selectors[0].match_labels == {"team": "team-billing"}

    assert selectors[1].directory == "dev"
    assert selectors[1].match_labels == {"env": "dev", "type": "terraform"}

    # Write and compare with the original asset file
    expected = yaml.safe_load(asset_file.read_text())
    sdk.write_destination_selectors(selectors)
    out = yaml.safe_load((ks.OUTPUT_DIR / "destination_selectors.yaml").read_text())
    assert out == expected


def test_env_vars_exposed(monkeypatch):
    monkeypatch.setenv("KRATIX_WORKFLOW_ACTION", "backstage-configure")
    monkeypatch.setenv("KRATIX_WORKFLOW_TYPE", "backstage-resource")
    monkeypatch.setenv("KRATIX_PROMISE_NAME", "postgres-ha")
    monkeypatch.setenv("KRATIX_PIPELINE_NAME", "configure-database")

    sdk = ks.KratixSDK()
    assert sdk.workflow_action() == "backstage-configure"
    assert sdk.workflow_type() == "backstage-resource"
    assert sdk.promise_name() == "postgres-ha"
    assert sdk.pipeline_name() == "configure-database"

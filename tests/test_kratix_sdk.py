import yaml
import pytest
from pathlib import Path

import kratix_sdk as ks


# ---------- Helpers ----------


@pytest.fixture(autouse=True)
def reset_dirs(tmp_path):
    """
    Keep global dirs isolated per test.
    """
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    meta_dir = tmp_path / "meta"
    in_dir.mkdir()
    out_dir.mkdir()
    meta_dir.mkdir()
    ks.set_input_dir(in_dir)
    ks.set_output_dir(out_dir)
    ks.set_metadata_dir(meta_dir)
    yield


# ---------- Status Tests ----------


def test_status_read_and_write(tmp_path):
    assets = Path(__file__).parent / "assets"
    src = assets / "status.yaml"
    expected_after_update = assets / "updated-status.yaml"
    assert src.exists(), f"Missing asset: {src}"
    assert expected_after_update.exists(), f"Missing asset: {expected_after_update}"

    ks.set_metadata_dir(assets)
    sdk = ks.KratixSDK()
    st = sdk.read_status()

    conditions = st.get("conditions")
    assert isinstance(conditions, list)
    assert conditions[0]["type"] == "Ready"
    assert conditions[0]["status"] == "True"
    assert st.get("observedGeneration") == 3
    assert st.get("message") == "first-pipeline"
    assert st.get("temp-key") == "temp-value"

    st.set("message", "second-pipeline")
    st.remove("temp-key")

    out_meta = tmp_path / "metadata"
    out_meta.mkdir(parents=True, exist_ok=True)
    ks.set_metadata_dir(out_meta)
    sdk.write_status(st)

    written = yaml.safe_load((out_meta / "status.yaml").read_text()) or {}
    expected = yaml.safe_load(expected_after_update.read_text()) or {}
    assert written == expected


def test_status_get_empty_key():
    root = {"a": {"b": 1, "c": {"d": 2}}}
    s = ks.Status(root)
    assert s.get("") is root


def test_status_get_missing_key():
    s = ks.Status({"a": {"b": 1}, "c": {"d": 2}})
    with pytest.raises(KeyError):
        s.get("a.c.e")


def test_status_get_descend_into_non_map():
    s = ks.Status({"e": 1})
    with pytest.raises(KeyError):
        s.get("e.b")


def test_status_set_empty_key():
    s = ks.Status({})
    with pytest.raises(ValueError):
        s.set("", 123)


def test_status_set_non_map_key():
    s = ks.Status({"a": 1})
    with pytest.raises(TypeError):
        s.set("a.b", 2)


def test_status_remove_empty_key():
    s = ks.Status({"a": {"b": 1}})
    with pytest.raises(ValueError):
        s.remove("")


def test_status_remove_missing_key():
    s = ks.Status({"a": {"b": 1}})
    with pytest.raises(KeyError):
        s.remove("a.c")


# ---------- Rsource Tests ----------


def test_resource_input_read():
    assets_dir = Path(__file__).parent / "assets"
    src = assets_dir / "object.yaml"
    assert src.exists(), f"Missing asset: {src}"
    ks.set_input_dir(assets_dir)

    sdk = ks.KratixSDK()
    r = sdk.read_resource_input()

    assert isinstance(r, ks.Resource)
    assert r.get_value("spec.size") == "small"
    assert r.get_name() == "example"
    assert r.get_namespace() == "default"
    assert r.get_labels() == {"app": "example"}
    assert r.get_annotations() == {
        "test.kratix.io/annotation": "This is a test annotation"
    }

    # GVK
    gvk = r.get_group_version_kind()
    assert (gvk.group, gvk.version, gvk.kind) == (
        "marketplace.kratix.io",
        "v1alpha1",
        "redis",
    )


# ---------- Promise Tests ----------


def test_promise_input_read():
    assets = Path(__file__).parent / "assets" / "promise"
    src = assets / "object.yaml"
    assert src.exists(), f"Missing asset: {src}"
    ks.set_input_dir(assets)

    sdk = ks.KratixSDK()
    p = sdk.read_promise_input()

    assert isinstance(p, ks.Promise)
    assert p.get_name() == "namespace"
    assert p.get_labels() == {"kratix.io/promise-version": "v0.1.0"}
    assert p.get_annotations() == {}


# ---------- Destination Selectors Tests ----------


def test_destination_selectors_read_write(tmp_path):
    assets_dir = Path(__file__).parent / "assets"
    asset_file = assets_dir / "destination-selectors.yaml"
    assert asset_file.exists(), f"Missing test asset: {asset_file}"

    ks.set_metadata_dir(assets_dir)
    sdk = ks.KratixSDK()

    selectors = sdk.read_destination_selectors()
    assert selectors[0].directory == "prod"
    assert selectors[0].match_labels == {"team": "team-billing"}
    assert selectors[1].directory == "dev"
    assert selectors[1].match_labels == {"env": "dev", "type": "terraform"}

    # Write to a temp METADATA_DIR and compare to the asset
    out_meta = tmp_path / "metadata"
    out_meta.mkdir(parents=True, exist_ok=True)
    ks.set_metadata_dir(out_meta)

    expected = yaml.safe_load(asset_file.read_text())
    sdk.write_destination_selectors(selectors)

    written = yaml.safe_load((out_meta / "destination-selectors.yaml").read_text())
    assert written == expected


# ---------- Envvars Tests ----------


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


def test_is_promise_workflow(monkeypatch):
    sdk = ks.KratixSDK()

    monkeypatch.setenv("KRATIX_WORKFLOW_TYPE", "promise")
    assert sdk.is_promise_workflow() is True

    monkeypatch.setenv("KRATIX_WORKFLOW_TYPE", "resource")
    assert sdk.is_promise_workflow() is False


def test_is_resource_workflow(monkeypatch):
    sdk = ks.KratixSDK()

    monkeypatch.setenv("KRATIX_WORKFLOW_TYPE", "resource")
    assert sdk.is_resource_workflow() is True

    monkeypatch.setenv("KRATIX_WORKFLOW_TYPE", "promise")
    assert sdk.is_resource_workflow() is False


def test_is_configure_action(monkeypatch):
    sdk = ks.KratixSDK()

    monkeypatch.setenv("KRATIX_WORKFLOW_ACTION", "configure")
    assert sdk.is_configure_action() is True

    monkeypatch.setenv("KRATIX_WORKFLOW_ACTION", "delete")
    assert sdk.is_configure_action() is False


def test_is_delete_action(monkeypatch):
    sdk = ks.KratixSDK()

    monkeypatch.setenv("KRATIX_WORKFLOW_ACTION", "delete")
    assert sdk.is_delete_action() is True

    monkeypatch.setenv("KRATIX_WORKFLOW_ACTION", "configure")
    assert sdk.is_delete_action() is False


# ---------- Write to Output Tests ----------


def test_write_output(tmp_path):
    ks.set_output_dir(tmp_path / "out")
    sdk = ks.KratixSDK()
    manifest_path = "nested/dir/deployment.yaml"
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "nginx",
        },
        "spec": {
            "replicas": 1,
            "template": {
                "spec": {
                    "containers": [
                        {
                            "image": "nginx:1.25",
                        }
                    ]
                },
            },
        },
    }

    data = yaml.safe_dump(manifest).encode("utf-8")
    sdk.write_output(manifest_path, data)

    dest = ks.get_output_dir() / manifest_path
    assert dest.parent == ks.get_output_dir() / "nested" / "dir"
    assert dest.is_file()
    written = yaml.safe_load(dest.read_text())
    assert written == manifest
    assert written["kind"] == "Deployment"
    assert written["metadata"]["name"] == "nginx"
    assert written["spec"]["template"]["spec"]["containers"][0]["image"] == "nginx:1.25"

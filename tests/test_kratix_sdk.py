import yaml
import pytest
from pathlib import Path

import kratix_sdk as ks


# ---------- Helpers ----------


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(data, f)

@pytest.fixture(autouse=True)
def reset_dirs(tmp_path, monkeypatch):
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


# ---------- Tests ----------

def test_status_read_and_write(tmp_path):
    assets = Path(__file__).parent / "assets"
    src = assets / "status.yaml"
    expected_after_update = assets / "updated-status.yaml"
    assert src.exists(), f"Missing asset: {src}"
    assert expected_after_update.exists(), f"Missing asset: {expected_after_update}"

    out_dir = tmp_path / "out"
    ks.set_output_dir(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "status.yaml").write_text(src.read_text())

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
    sdk.write_status(st)

    written = yaml.safe_load((out_dir / "status.yaml").read_text()) or {}
    expected = yaml.safe_load(expected_after_update.read_text()) or {}
    assert written == expected


def test_resource_input_read():
    asset = Path(__file__).parent / "assets" / "object.yaml"
    obj = yaml.safe_load(asset.read_text())
    r = ks.Resource(obj)

    assert r.get_value("spec.size") == "small"

    # metadata
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


def test_destination_selectors_read_write(tmp_path):
    assets_dir = Path(__file__).parent / "assets"
    asset_file = assets_dir / "destination_selectors.yaml"
    assert asset_file.exists(), f"Missing test asset: {asset_file}"

    ks.set_input_dir(assets_dir)
    ks.set_output_dir(tmp_path / "out")
    ks.get_output_dir().mkdir(parents=True, exist_ok=True)

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
    out = yaml.safe_load(
        (ks.get_output_dir() / "destination_selectors.yaml").read_text()
    )
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

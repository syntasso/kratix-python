import yaml
import pytest
from pathlib import Path

import kratix_sdk as ks


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

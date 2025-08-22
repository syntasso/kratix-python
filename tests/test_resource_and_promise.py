from pathlib import Path

import pytest
import kratix_sdk as ks

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
    with pytest.raises(KeyError):
        r.get_value("does_not_exist")
    assert r.get_value("does_not_exist", default="default") == "default"
    assert r.get_value("spec.age", default=None) is None
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

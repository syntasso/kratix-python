import yaml
import kratix_sdk as ks

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

import sys
import kratix_sdk as ks
from typing import List
import yaml

def promise_configure() -> int:
    sdk = ks.KratixSDK()
    print("Helper variables:")
    print("Workflow action: ", sdk.workflow_action())
    print("Workflow type: ", sdk.workflow_type())
    print("Promise name: ", sdk.promise_name())
    print("Workflow action: ", sdk.pipeline_name())

    print("Reading Promise input...")
    promise = sdk.read_promise_input()
    name = promise.get_name()
    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": name + "-config", "namespace": "default"},
        "data": {
            "workflowAction": sdk.workflow_action(),
            "workflowType": sdk.workflow_type(),
            "promiseName": name,
            "pipelineName": sdk.pipeline_name(),
        },
    }
    data = yaml.safe_dump(manifest).encode("utf-8")
    sdk.write_output("config.yaml", data)

    print("All tests passed")
    return 0

def resource_configure() -> int:
    sdk = ks.KratixSDK()
    print("Helper variables:")
    print("Workflow action: ", sdk.workflow_action())
    print("Workflow type: ", sdk.workflow_type())
    print("Promise name: ", sdk.promise_name())
    print("Workflow action: ", sdk.pipeline_name())

    print("Reading Resource input...")
    resource = sdk.read_resource_input()

    print("Getting fields...")
    fields = resource.get_value("spec.fields")
    print("Fields: ", fields)
    
    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": resource.get_name() + "-config", "namespace": resource.get_namespace()},
        "data": {
            "workflowAction": sdk.workflow_action(),
            "workflowType": sdk.workflow_type(),
            "promiseName": sdk.promise_name(),
            "pipelineName": sdk.pipeline_name(),
        },
    }
    for field in fields:
        manifest["data"][field["name"]] = field["value"]

    data = yaml.safe_dump(manifest).encode("utf-8")
    sdk.write_output("config.yaml", data)

    print("Publishing 'publishedDirectly' status...")
    status = ks.Status()
    status.set("publishedDirectly", True)
    sdk.publish_status(resource, status)

    print("Wrtiting status file...")
    status = ks.Status()
    status.set("viaFile", True)
    sdk.write_status(status)
    print("Validating status file...")
    status = sdk.read_status()
    if not status.get("viaFile"):
        print("Status file validation failed: 'viaFile' is not True", file=sys.stderr)
        return 1

    print("Validating destination selectors...")
    selectors: List[ks.DestinationSelector] = [
        ks.DestinationSelector(match_labels={"environment": "dev"})
    ]
    sdk.write_destination_selectors(selectors)

    selectors = sdk.read_destination_selectors()
    if len(selectors) != 1:
        print("Destination selectors validation failed: expected 1 selector, got", len(selectors), file=sys.stderr)
        return 1
    if selectors[0].match_labels["environment"] != "dev": 
        print("Destination selectors validation failed: expected 'environment=dev', got", selectors[0].match_labels, file=sys.stderr)
        return 1


    print("All tests passed")
    return 0


def main() -> int:
    # Dispatch by argv[1]
    if len(sys.argv) < 2:
        print("usage: handlers.py [promise-configure|resource-configure]", file=sys.stderr)
        return 2

    cmd = sys.argv[1]
    if cmd == "promise-configure":
        return promise_configure()
    if cmd == "resource-configure":
        return resource_configure()

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

import kratix_sdk as ks
import yaml

def main():
    sdk = ks.KratixSDK()
    resource = sdk.read_resource_input()
    name = resource.get_name()
    size = resource.get_value("spec.size")

    manifest = {
        "apiVersion": "acid.zalan.do/v1",
        "kind": "postgresql",
        "metadata": {"name": name, "namespace": "default"},
        "spec": {
        	"teamId": "kratix",
			"enableLogicalBackup": True,
        	"volume": {
            	"size": size
        	},
        	"numberOfInstances": 2,
                "users": {
                     "team-a": ["superuser", "createdb"]
                },
        	"postgresql": {
            	"version": "16"
        	}
		}
    }
    data = yaml.safe_dump(manifest).encode("utf-8")
    sdk.write_output("database.yaml", data)

    status = ks.Status()
    status.set("version", 16)
    status.set("teamId", "kratix")
    sdk.write_status(status)


if __name__ == '__main__':
    main()
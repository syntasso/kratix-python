from typing import Dict

class Promise:
    def get_name(self) -> str:
        return self.data.get("metadata", {}).get("name", "")
    def get_labels(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("labels", {})

    def get_annotations(self) -> Dict[str, str]:
        return self.data.get("metadata", {}).get("annotations", {})
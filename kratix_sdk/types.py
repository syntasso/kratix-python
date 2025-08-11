from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class GroupVersionKind:
    group: str
    version: str
    kind: str

@dataclass
class DestinationSelector:
    directory: str
    match_labels: Dict[str, Any] = field(default_factory=dict)
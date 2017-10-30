import json
from typing import Dict, Union

Interfaces = Dict[str, Dict[str, Union[str, int]]]


def read_interfaces(path: str) -> Interfaces:
	with open(path, encoding='utf-8') as f:
		return json.load(f)

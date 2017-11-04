import json
import logging
from typing import Dict, Set, Union

Interfaces = Dict[str, Dict[str, Union[str, int]]]


def read_interfaces(path: str) -> Interfaces:
	with open(path, encoding='utf-8') as f:
		return json.load(f)


def factors(number: int, limit: int) -> Set[int]:
	return {x for x in [2**x for x in range(limit)] if number % x == 0}


def multiple(number: int, limit: int) -> Set[str]:
	return {str(x).zfill(2) for x in [2**x for x in range(limit)] if x % 2**(number-1) == 0}


def setup_logging():
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=5
	)

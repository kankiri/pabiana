from collections import deque
from typing import Iterable, MutableMapping

from pabiana.abcs import Area


def init_full(area: Area, source: str, slots: Iterable[str]=None):
	if slots is None:
		area.context[source] = deque(maxlen=100)
	else:
		area.context[source] = {}
		for slot in slots:
			area.context[source][slot] = deque(maxlen=100)


def imprint_full(area: Area, source: str, message: MutableMapping, slot: str=None):
	if slot is None:
		area.context[source].appendleft(message)
		area.context[source][0]['time-rcvd'] = area.time
		return {'recent': area.context[source][0], 'section': area.context[source]}
	else:
		area.context[source][slot].appendleft(message)
		area.context[source][slot][0]['time-rcvd'] = area.time
		return {'recent': area.context[source][slot][0], 'section': area.context[source][slot]}


def reference_full(area: Area, source: str, slot: str=None):
	if slot is None:
		return {'recent': area.context[source][0], 'section': area.context[source]}
	else:
		return {'recent': area.context[source][slot][0], 'section': area.context[source][slot]}

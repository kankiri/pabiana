from collections import deque
from . import area


def init_simple(area_name, slot):
	area.context[name][slot] = None


def imprint_simple(area_name, slot, message):
	area.context[area_name][slot] = message


def natural(name, slot, message):
	for key in message:
		try:
			area.context[name][slot][key].append(area.clock)
		except KeyError:
			area.context[name][slot][key] = deque(maxlen=length_parameter)
			area.context[name][slot][key].append(area.clock)
		except TypeError:
			area.context[name][slot] = {}
			natural(name, slot, message)


def comprehensive(name, slot, message):
	for key in message:
		try:
			if message[key] in area.context[name][slot][key]:
				area.context[name][slot][key][message[key]].append(area.clock)
			else:
				area.context[name][slot][key][message[key]] = deque(maxlen=length_parameter)
				area.context[name][slot][key][message[key]].append(area.clock)
		except KeyError:
			area.context[name][slot][key] = {}
			area.context[name][slot][key][message[key]] = deque(maxlen=length_parameter)
			area.context[name][slot][key][message[key]].append(area.clock)
		except TypeError:
			area.context[name][slot] = {}
			comprehensive(name, slot, message)


def inverted(name, slot, message):
	for key in message:
		try:
			area.context[name][slot][key].append((area.clock, message[key]))
		except KeyError:
			area.context[name][slot][key] = deque(maxlen=3*length_parameter)
			area.context[name][slot][key].append((area.clock, message[key]))
		except TypeError:
			area.context[name][slot] = {}
			inverted(name, slot, message)

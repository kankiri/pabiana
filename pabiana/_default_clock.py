from . import Clock


clock = Clock('clock', host='0.0.0.0')
config = {
	'timeout': 1000,
	'use-template': True
}

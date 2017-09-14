#!/usr/bin/env python3

import logging

from pabiana import Clock

NAME = 'clock'


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	clock = Clock(NAME, host='0.0.0.0')
	clock.setup(timeout=1000, use_template=True)
	clock.run()


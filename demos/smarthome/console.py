#!/usr/bin/env python3

import json
import logging
import signal

from pabiana import create_publisher, load_interfaces, trigger

NAME = 'console'
publisher = None
stop = None


def _signal_handler(signum, frame):
	global stop
	stop = True


def main():
	global stop
	stop = False
	signal.signal(signal.SIGINT, _signal_handler)
	try:
		while not stop:
			s = input('--> ').lower()
			if 'quit' in s:
				raise KeyboardInterrupt
			if 'open' in s:
				data = {'signal': 'window-open'}
				publisher.send_multipart(['input'.encode('utf-8'), json.dumps(data).encode('utf-8')])
			elif 'close' in s:
				data = {'signal': 'window-close'}
				publisher.send_multipart(['input'.encode('utf-8'), json.dumps(data).encode('utf-8')])
	finally:
		trigger('association', 'exit')
		trigger('smarthome', 'exit')
		trigger('weather', 'exit')
		trigger('clock', 'exit')


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	main()

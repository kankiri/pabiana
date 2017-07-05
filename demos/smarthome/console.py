#!/usr/bin/env python3

import json
import logging

from pabiana.area import load_interfaces
from pabiana.node import create_publisher, trigger

NAME = 'console'
publisher = None


def main():
	try:
		while True:
			s = input('--> ').lower()
			if 'quit' in s:
				raise KeyboardInterrupt
			if 'open' in s:
				data = {'signal': 'window-open'}
				publisher.send_multipart(['input'.encode('utf-8'), json.dumps(data).encode('utf-8')])
			elif 'close' in s:
				data = {'signal': 'window-close'}
				publisher.send_multipart(['input'.encode('utf-8'), json.dumps(data).encode('utf-8')])
	except KeyboardInterrupt:
		trigger('association', 'shutdown')
		trigger('smarthome', 'shutdown')
		trigger('weather', 'shutdown')


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	main()

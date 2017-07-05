#!/usr/bin/env python3

import logging
import time

from pabiana.area import load_interfaces
from pabiana.node import create_publisher

NAME = 'pulse'
publisher = None


def main():
	clock = 1
	message = '{}'.encode('utf-8')
	
	while True:
		publisher.send_multipart(['01'.encode('utf-8'), message])
		if clock % 2 == 0:
			publisher.send_multipart(['02'.encode('utf-8'), message])
			if clock % 4 == 0:
				publisher.send_multipart(['04'.encode('utf-8'), message])
				if clock % 8 == 0:
					publisher.send_multipart(['08'.encode('utf-8'), message])
					if clock % 16 == 0:
						publisher.send_multipart(['16'.encode('utf-8'), message])
						if clock % 32 == 0:
							publisher.send_multipart(['32'.encode('utf-8'), message])
		clock += 1
		time.sleep(1)


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	main()

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
	name='Pabiana',
	version='0.0.1',
	packages=find_packages(),
	install_requires=['pyzmq']
)

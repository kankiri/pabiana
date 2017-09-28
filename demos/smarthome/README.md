This program is used to demonstrate the convenient way to write and run software using the Pabiana framework.
It works the same way as the program found in the *smarthome* folder, but needs less code.

## Installation

Create a virtual environment and run

    pip install --upgrade -r requirements.txt

from within it.

## Usage

The program consists of 4 parts (Areas), each of which should be run in a different process.
To run one of them, use:

    python3 -m pabiana weather:weather

The first *weather* part of the parameter specifies the folder name of the submodule.
The second part specifies the Area name, which is the same as the first one in this example.

You can also start more than one Area with a single command.

    python3 -m pabiana weather:weather smarthome:smarthome

Make sure to start at least the optional *console* Area with it's own command, because it waits for user input.


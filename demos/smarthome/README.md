This program is used to demonstrate the convenient way to write and run software using the Pabiana framework.

## Installation

Create a virtual environment and run

    pip install --upgrade -r requirements.txt

from within it.

## Usage

The program consists of 4 parts (Areas), each of which should be run in a different process.
To run one of them, use:

    python3 -m pabiana weather:weather

The first *weather* part of the parameter specifies the folder name of the submodule.
The second part specifies the Area name, which is identical in this example.

You can also start more than one Area with a single command.

    python3 -m pabiana weather:weather smarthome:smarthome

Besides *weather* and *smarthome*, there are also the *association* and *console* Areas.
Make sure to start at least the optional *console* Area with it's own command, because it waits for user input.
For the application to work properly, you also have to start a Clock.
Append *-C* to one of the commands, to do so.

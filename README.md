# Python ASCII Tetris clone

Tetris game with an ASCII GUI. Built with Python 3.5.2.

## Functionality

Number of rows and columns can be arbitrary. Levels span from 1 to 10. Scoring system in accordance with [http://tetris.wikia.com/wiki/Scoring](http://tetris.wikia.com/wiki/Scoring).

## Usage

Run the file "main.py" from the console. Game defaults as a 20 x 10 grid, with level set to 1. This can be changed by editing the last
line of "main.py":


	if __name__ == '__main__':
	
		main_loop(m, n, L)

where m = number of rows, n = number of columns, L = level.

## Modules

- constants.py - dictionaries and variables containing block definitions, scoring and level system
- main.py - classes and functions

## Dependencies outside the standard library

- numpy

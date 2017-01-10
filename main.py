"""
Created on Sat Dec 31 12:02:57 2016

@author: Radovan
"""

# external imports
from msvcrt import getch, kbhit
import numpy as np
import time
import os
from random import choice, seed
import winsound

# internal imports
from constants import *

####################            
# CLASSES
####################
class Board:
    
    # representation
    # --------------
    def __init__(self, dim_x, dim_y, level):
        """
            Board dimensions and representation
            dim_x ... number of rows
            dim_y ... number of columns
        """
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.board_array = np.zeros((dim_x, dim_y))
        self.fallen = False
        self.score = 0
        self.rows_cleared = 0
        self.level = level
        self.tick = GAME_TICK_DICT[self.level]
        self.sound = True
       
    def mark_squares(self, squares, state=2):
        """
            Marks multiple squares on the board
            as occupied. First argument is a tuple of tuples,
            second arg is 1 for static block, 2 for falling block
        """
        if state == 1:
            for square in squares:
                self.board_array[square[0]][square[1]] = 1
        else:
            for square in squares:
                self.board_array[square[0]][square[1]] = 2

    def unmark_squares(self, squares):
        """
            UnMarks multiple squares on the board
            as occupied. Argument is a tuple of tuples
        """
        for square in squares:
            self.board_array[square[0]][square[1]] = 0

    def check_marked_rows(self):
        """
            Returns indices of completely marked
            rows
        """       
        marked_rows = [index for index in range(self.dim_x) if np.count_nonzero(self.board_array[index]) == self.dim_y]
        return marked_rows
    
    def drop_marked_rows(self):
        """
            Removes completely marked rows and replaces
            them with upper rows; updates score
        """
        indices = sorted(self.check_marked_rows())
        if indices != []:
            n = len(indices)
            self.play_sound_drop(540, 30)
            for index in indices:
                i = 0
                while np.any(self.board_array[index - (i + 1)] != 0):
                    self.board_array[index - i] = self.board_array[index - (i + 1)]                    
                    i += 1
                self.board_array[index - i] = self.board_array[index - (i + 1)]
            self.score += GAME_SCORE_DICT[n]*self.level
            self.rows_cleared += n

    def check_squares(self, squares):
        """
            Checks is squares are available to place block
        """
        for square in squares:
            if square[0] >= self.dim_x or square[1] >= self.dim_y:                
                return False
            if square[0] < 0 or square[1] < 0:                
                return False
            if self.board_array[square[0]][square[1]] == 1:
                return False
        return True
        
    # block methods
    # ----------------        
    def add_block(self, block, falling=True):
        """
            Adds block object to board
        """
        block_coords = block.absolute_coords     
        if self.check_squares(block_coords) == False:
                return 0           
        if falling == False:
            self.mark_squares(block_coords, 1)
        else:
            self.mark_squares(block_coords, 2)            
        
    def move_block_down(self, block):
        """
            Moves block down by 1 step
        """
        block_coords = block.absolute_coords
        new_block = Block(block.x + 1, block.y, block.type, block.rotation)
        if self.add_block(new_block) == 0:
            self.add_block(block, falling=False)
            self.fallen = True
            self.play_sound_fall(200, 25)
            self.drop_marked_rows()
        else:
            self.unmark_squares(block_coords)
            self.mark_squares(new_block.absolute_coords)
            block.move_down()
            # check if block is on bottom
            new_block2 = Block(new_block.x + 1, new_block.y, new_block.type, new_block.rotation)    
            if self.check_squares(new_block2.absolute_coords) == False:
                self.add_block(new_block, falling=False)
                self.fallen = True           
                self.play_sound_fall(200, 25)
                self.drop_marked_rows()
                
    def move_block_left(self, block):
        """
            Moves block left by 1 step
        """
        block_coords = block.absolute_coords
        new_block = Block(block.x, block.y - 1, block.type, block.rotation)
        if self.add_block(new_block) != 0:
            self.unmark_squares(block_coords)
            self.mark_squares(new_block.absolute_coords)
            block.move_left()                 

    def move_block_right(self, block):
        """
            Moves block right by 1 step
        """
        block_coords = block.absolute_coords
        new_block = Block(block.x, block.y + 1, block.type, block.rotation)
        if self.add_block(new_block) != 0:
            self.unmark_squares(block_coords)
            self.mark_squares(new_block.absolute_coords)
            block.move_right()              

    def rotate_block(self, block):
        """
            Rotate block
        """
        block_coords = block.absolute_coords
        new_block = Block(block.x, block.y, block.type, block.rotation)
        new_block.rotate()
        if self.add_block(new_block) != 0:
            self.unmark_squares(block_coords)
            self.mark_squares(new_block.absolute_coords)
            block.rotate()
            
    def drop_block(self, block):
        """
            Drop block down
        """
        while self.fallen == False:
            self.move_block_down(block)
            
    # graphics & sound
    # -------------------
    def draw_row(self, row_index):
        """
            Returns string representing selected row
        """
        row_string = '|'
        for i in range(self.dim_y):
            if self.board_array[row_index][i] == 0:
                row_string += ' .'
            else:
                row_string += '[]'
        row_string += '|'
        return row_string

    def draw_board(self):
        """
            Returns string representing the board, score, level
            and other info
        """
        board_string = '\n'
        for i in range(self.dim_x):
            board_string += self.draw_row(i)
            board_string += '\n'
        board_string += '+' + self.dim_y*'--' + '+\n'
        board_string += '\nLEVEL: {}\n'.format(self.level)
        board_string += 'ROWS CLEARED: {}\n'.format(self.rows_cleared)
        board_string += 'SCORE: {}\n'.format(self.score)
        board_string += '\n[ ARROWS - left/right/down/rotate | SPACE - Drop | S - Sound on/off | ESC - exit ]\n'        
      
        print(board_string)
        
    def play_sound_drop(self, freq, dur):
        if self.sound == True:
            winsound.Beep(freq, dur)

    def play_sound_fall(self, freq, dur):
        if self.sound == True:
            winsound.Beep(freq, dur)        
        
class Block:
    
    def __init__(self, x, y, block_type, block_rotation):
        self.x = x
        self.y = y
        self.type = block_type
        self.rotation = block_rotation
        self.relative_coords = BLOCK_DICT[block_type][block_rotation]
        self.absolute_coords = tuple(((self.x + item[0], self.y + item[1]) for item in self.relative_coords))

    def update_relative_coordinates(self):
        self.relative_coords = BLOCK_DICT[self.type][self.rotation]
        
    def update_absolute_coordinates(self):        
        self.absolute_coords = tuple(((self.x + item[0], self.y + item[1]) for item in self.relative_coords))
        
    def move_down(self):
        self.x += 1
        self.update_absolute_coordinates()

    def move_left(self):
        self.y -= 1
        self.update_absolute_coordinates()

    def move_right(self):
        self.y += 1
        self.update_absolute_coordinates()

    def rotate(self):
        number_of_rotations = len(BLOCK_DICT[self.type])
        if number_of_rotations > 1:
            if self.rotation < number_of_rotations:
                self.rotation += 1
            else:
                self.rotation = 1
            self.update_relative_coordinates()
            self.update_absolute_coordinates()        

class Game:

    def __init__(self, board_rows=20, board_columns=10, level=1):
        self.board_rows = board_rows
        self.board_columns = board_columns
        self.level = level

    def create_random_block(self, board):
        """
            Creates random block at upper
            center of board
        """
        seed()
        my_type = choice(list(BLOCK_DICT.keys()))
        my_rot = choice(list(BLOCK_DICT[my_type].keys()))
        my_y = int(board.dim_y/2)
        my_x = 2
        my_block = Block(my_x, my_y, my_type, my_rot)
        return my_block
   
    def refresh_graphics(self, board):
        """
            Clears the screen and draws the board
        """
        os.system('cls')
        board.draw_board()

    def show_menu(self):
        """
            Main menu
        """
        while True:
            os.system('cls')
            print('\nMAIN MENU')
            print('---------')
            print('\n1 - Start game')
            print('\n2 - Set level')
            print('\n3 - Set grid')
            print('\n4 - Exit')
            key = ord(getch())
            if key == 49:
                self.start()
            elif key == 50:
                level = input("\nEnter Level (1 - 10): ")
                self.level = int(level)
            elif key == 51:
                rows = input("\nEnter number of rows: ")
                cols = input("\nEnter number of columns: ")
                self.board_rows, self.board_columns = int(rows), int(cols)
            elif key == 52:
                os.system('cls')
                break
            else:
                pass


    def start(self):
        """
            Starts the game
        """
        b = Board(self.board_rows, self.board_columns, self.level)
        b1 = self.create_random_block(b)
        b.add_block(b1)
        self.refresh_graphics(b)

        t1 = time.clock()

        game_loop = True
        while game_loop == True:

            while not kbhit():

                if b.fallen == True:
                    b.fallen = False
                    b1 = self.create_random_block(b)
                    if b.add_block(b1) == 0:
                        print("G A M E  O V E R")
                        game_loop = False
                        break

                t2 = time.clock()
                if t2 - t1 > b.tick:
                    t1 = time.clock()
                    b.move_block_down(b1)
                    self.refresh_graphics(b)
                time.sleep(SYSTEM_TICK)

            if game_loop == False:
                break

            key = ord(getch())
            if key == 75:
                b.move_block_left(b1)
            elif key == 77:
                b.move_block_right(b1)
            elif key == 80:
                b.move_block_down(b1)
            elif key == 72:
                b.rotate_block(b1)
            elif key == 32:
                b.drop_block(b1)
            elif key == 115 or key == 83:
                b.sound = not b.sound
            elif key == 27:
                break
            else:
                pass
            self.refresh_graphics(b)


            
if __name__ == '__main__':

    g = Game()
    g.show_menu()
        
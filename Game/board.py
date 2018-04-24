from . import utils
from . import color
from . import piece

from copy import deepcopy
import pygame


class Board:

    def __init__(self, size, color1=color.WHITE, color2=color.GREY, king=None):
        # note: state is row col system
        self.size = size  # set the number of rows/cols of the board.
        self.color1 = color1  # can customize color of tiles.
        self.color2 = color2  # can customize color of tiles.
        self.state = [[None for _ in range(size)] for _ in range(size)]  # state that maintains location of all pieces
        self.king = king  # pygame image object of the king icon.

        # checker board, row col system, used to render colors.
        # 0 indicates color1, 1 indicates color2 & 2 indicates highlight
        self.cboard = utils.generate_checker_board(size)

    def get_copy(self):
        """Returns a copy of the Board object. workaround for pygame surface object and deepcopy incompatibility"""
        new_board = Board(size=self.size, color1=self.color1, color2=self.color2)
        new_board.state = deepcopy(self.state)

        return new_board

    def render(self, output, rect_pos, circle_pos):
        """Method to render the board and it's contents on the screen"""
        for row in range(self.size):
            for col in range(self.size):
                '''Pygame coordinate system is x(->), y(v). But accessing arrays is more like row(v), column(->)'''
                x, y = col, row

                if self.cboard[row][col] == 1:
                    tile_color = self.color1
                elif self.cboard[row][col] == 2:
                    tile_color = color.GREEN
                else:
                    tile_color = self.color2

                # Draw the tile on the screen
                pygame.draw.rect(output, tile_color, rect_pos[(x, y)] + [100, 100])

                if type(self.state[row][col]) is piece.Piece:
                    # if the tile has a piece on it, render it too.
                    self.state[row][col].render_piece(output, circle_pos)
                    if self.state[row][col].king:
                        # if the piece is a king, render the king icon too
                        output.blit(self.king, rect_pos[(x, y)])

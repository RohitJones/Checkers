from . import color
from pygame import gfxdraw


class Piece:
    def __init__(self, piece_id, position, piece_color, direction):
        # note: position is Row Col system
        self.color = piece_color
        self.direction = direction
        self.id = piece_id
        self.position = position
        self.king = False

    def render_piece(self, output, circle_pos):
        # note: rendering is XY system
        y, x = circle_pos[self.position]

        # Experimental features PyGame may break it in the future
        gfxdraw.filled_circle(output, x, y, 32, self.color)
        gfxdraw.aacircle(output, x, y, 32, color.BLACK)
        gfxdraw.aacircle(output, x, y, 31, color.BLACK)

        # Standard method
        # pygame.draw.circle(output, self.color, (x, y), 30)

    def possible_moves(self, game_board):
        # used to store possible moves. If a move is a kill move,
        # the value of the move key is the location of the killed piece
        normal_moves = {}
        kill_moves = {}

        row, col = self.position

        if (self.direction == 'up' or self.king) and row - 1 >= 0:
            # Left Diagonal
            if col - 1 >= 0 and game_board.state[row - 1][col - 1] is None:
                normal_moves[(row - 1, col - 1)] = None

            elif \
                    col - 2 >= 0 and row - 2 >= 0 and \
                    game_board.state[row - 1][col - 1].color != self.color and \
                    game_board.state[row - 2][col - 2] is None:

                kill_moves[(row - 2, col - 2)] = (row - 1, col - 1)

            # Right Diagonal
            if col + 1 <= (game_board.size - 1) and game_board.state[row - 1][col + 1] is None:
                normal_moves[(row - 1, col + 1)] = None

            elif \
                    col + 2 <= (game_board.size - 1) and row - 2 >= 0 and \
                    game_board.state[row - 1][col + 1].color != self.color and \
                    game_board.state[row - 2][col + 2] is None:

                kill_moves[(row - 2, col + 2)] = (row - 1, col + 1)

        if (self.direction == 'down' or self.king) and row + 1 <= (game_board.size - 1):
            # Left Diagonal
            if col - 1 >= 0 and game_board.state[row + 1][col - 1] is None:
                normal_moves[(row + 1, col - 1)] = None

            elif \
                    col - 2 >= 0 and row + 2 <= (game_board.size - 1) and \
                    game_board.state[row + 1][col - 1].color != self.color and \
                    game_board.state[row + 2][col - 2] is None:

                kill_moves[(row + 2, col - 2)] = (row + 1, col - 1)

            # Right Diagonal
            if col + 1 <= (game_board.size - 1) and game_board.state[row + 1][col + 1] is None:
                normal_moves[(row + 1, col + 1)] = None

            elif \
                    col + 2 <= (game_board.size - 1) and row + 2 <= (game_board.size - 1) and \
                    game_board.state[row + 1][col + 1].color != self.color and \
                    game_board.state[row + 2][col + 2] is None:

                kill_moves[(row + 2, col + 2)] = (row + 1, col + 1)

        return kill_moves if kill_moves else normal_moves

    def kill_moves(self, game_board):
        return {move: kill for (move, kill) in self.possible_moves(game_board).items() if kill}

    def __str__(self):
        return "{}".format(self.id)

    def __repr__(self):
        return " {} ".format(self.id)

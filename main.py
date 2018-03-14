import pygame

from pygame import gfxdraw
from sys import exit


class Color:
    RED = 255, 0, 0
    GREEN = 0, 255, 0
    BLUE = 30, 92, 191
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    PINK = 226, 174, 222


def generate_checker_board(size):
    return [
        [1 if x % 2 == 0 else 0 for x in range(size)]
        if y % 2 == 0
        else
        [0 if x % 2 == 0 else 1 for x in range(size)]

        for y in range(size)
    ]
    # return [
    #     [1, 0, 1, 0, 1, 0],
    #     [0, 1, 0, 1, 0, 1],
    #     [1, 0, 1, 0, 1, 0],
    #     [0, 1, 0, 1, 0, 1],
    #     [1, 0, 1, 0, 1, 0],
    #     [0, 1, 0, 1, 0, 1],
    # ]


class Board:
    # checker board, row col system, also used to render colors
    cboard = generate_checker_board(6)

    def __init__(self, size, color1=Color.WHITE, color2=Color.PINK):
        # note: state is row col system
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.state = [[None for _ in range(size)] for _ in range(size)]

        # hack to maintain a persistent value through multiple event loop
        self.selected_piece = None

    def render(self, output):
        for row in range(self.size):
            for col in range(self.size):
                '''Pygame coordinate system is x(>), y(v). But accessing arrays is more like row(v), column(>)'''
                x, y = col, row

                if Board.cboard[row][col] == 1:
                    color = self.color1
                elif Board.cboard[row][col] == 2:
                    color = Color.GREEN
                else:
                    color = self.color2

                pygame.draw.rect(output, color, RECT_POS[(x, y)] + [100, 100])

                if type(self.state[row][col]) is Piece:
                    self.state[row][col].render_piece(output)


class Piece:
    def __init__(self, piece_id, position, color, direction):
        # note: position is Row Col system
        self.color = color
        self.direction = direction
        self.id = piece_id
        self.position = position

    def render_piece(self, output):
        # note: rendering is XY system
        y, x = CIRCLE_POS[self.position]

        # Experimental features PyGame may break it in the future
        gfxdraw.filled_circle(output, x, y, 32, self.color)
        gfxdraw.aacircle(output, x, y, 32, Color.BLACK)
        gfxdraw.aacircle(output, x, y, 31, Color.BLACK)

        # Standard method
        # pygame.draw.circle(output, self.color, (x, y), 30)

    def possible_moves(self, game_board):
        moves = []
        row, col = self.position

        if self.direction == 'up' and row - 1 >= 0:
            # Left Diagonal
            if col - 1 >= 0 and game_board.state[row - 1][col - 1] is None:
                moves.append(((row - 1, col - 1), None))

            elif \
                    col - 2 >= 0 and row - 2 >= 0 and \
                    game_board.state[row - 1][col - 1].direction == 'down' and \
                    game_board.state[row - 2][col - 2] is None:

                # moves.append(((row - 2, col - 2), 'CAPTURE'))
                moves.append(((row - 2, col - 2), (row - 1, col - 1)))

            # Right Diagonal
            if col + 1 <= 5 and game_board.state[row - 1][col + 1] is None:
                moves.append(((row - 1, col + 1), None))

            elif \
                    col + 2 <= 5 and row - 2 >= 0 and \
                    game_board.state[row - 1][col + 1].direction == 'down' and \
                    game_board.state[row - 2][col + 2] is None:

                # moves.append(((row - 2, col + 2), 'CAPTURE'))
                moves.append(((row - 2, col + 2), (row - 1, col + 1)))

        elif self.direction == 'down' and row + 1 <= 5:
            # Left Diagonal
            if col - 1 >= 0 and game_board.state[row + 1][col - 1] is None:
                moves.append(((row + 1, col - 1), None))

            elif \
                    col - 2 >= 0 and row + 2 <= 5 and \
                    game_board.state[row + 1][col - 1].direction == 'up' and \
                    game_board.state[row + 2][col - 2] is None:

                # moves.append(((row + 2, col - 2), 'CAPTURE'))
                moves.append(((row + 2, col - 2), (row + 1, col - 1)))

            # Right Diagonal
            if col + 1 <= 5 and game_board.state[row + 1][col + 1] is None:
                moves.append(((row + 1, col + 1), None))

            elif \
                    col + 2 <= 5 and row + 2 <= 5 and \
                    game_board.state[row + 1][col + 1].direction == 'up' and \
                    game_board.state[row + 2][col + 2] is None:

                # moves.append(((row + 2, col + 2), 'CAPTURE'))
                moves.append(((row + 2, col + 2), (row + 1, col + 1)))

        return moves

    def __str__(self):
        return "{}".format(self.id)

    def __repr__(self):
        return " {} ".format(self.id)


def display_refresh(current_board, output):
    screen.fill(Color.BLACK)
    current_board.render(output)
    pygame.display.flip()
    pygame.time.Clock().tick(60)


def get_clicked_tile(search_x, search_y):
    for y_index in range(6):  # size of board
        for x_index in range(6):
            check_x, check_y = RECT_POS[(x_index, y_index)]
            if check_y <= search_y <= check_y + 100 and check_x <= search_x <= check_x + 100:
                row, col = y_index, x_index
                return row, col

    return -1, -1


def event_loop(game_board):

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN:

            x, y = pygame.mouse.get_pos()
            row, col = get_clicked_tile(x, y)

            if game_board.state[row][col]:
                if game_board.selected_piece != game_board.state[row][col]:
                    Board.cboard = generate_checker_board(6)
                    game_board.selected_piece = game_board.state[row][col]

                # Highlight possible moves
                for each_move in game_board.selected_piece.possible_moves(game_board):
                    (row, col), capture_location = each_move
                    game_board.cboard[row][col] = 2

            elif game_board.selected_piece and (row, col) in [x[0] for x in game_board.selected_piece.possible_moves(game_board)]:
                prev_row, prev_col = game_board.selected_piece.position
                game_board.state[prev_row][prev_col] = None

                game_board.selected_piece.position = (row, col)
                game_board.state[row][col] = game_board.selected_piece

                game_board.selected_piece = None
                Board.cboard = generate_checker_board(6)

            else:
                selected_piece = None
                Board.cboard = generate_checker_board(6)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        if event.type == pygame.QUIT:
            exit()


def init_game(size):
    board = Board(size=size)

    # Row Col system
    AI_positions = [(0, 1), (0, 3), (0, 5), (1, 0), (1, 2), (1, 4), (3, 2)]
    HUMAN_positions = [(4, 1), (4, 3), (4, 5), (5, 0), (5, 2), (5, 4), (2, 3)]

    for index, row_col in enumerate(AI_positions):
        row, col = row_col
        board.state[row][col] = Piece('B' + str(index), (row, col), Color.BLUE, 'down')

    for index, row_col in enumerate(HUMAN_positions):
        row, col = row_col
        board.state[row][col] = Piece('R' + str(index), (row, col), Color.RED, 'up')

    return board


if __name__ == "__main__":

    pygame.init()

    bsize = 6  # Board Size
    resolution = (bsize * 100 + (bsize + 1) * 2, bsize * 100 + (bsize + 1) * 2)
    screen = pygame.display.set_mode(resolution)

    RECT_POS = {}
    CIRCLE_POS = {}

    for y_val in range(bsize):
        for x_val in range(bsize):
            y_coordinate = ((2 * (y_val + 1)) + (100 * y_val))
            x_coordinate = ((2 * (x_val + 1)) + (100 * x_val))
            RECT_POS[(x_val, y_val)] = [x_coordinate, y_coordinate]

            circle_y_coordinate = (2 * (y_val + 1)) + (100 * y_val) + 100 // 2
            circle_x_coordinate = (2 * (x_val + 1)) + (100 * x_val) + 100 // 2
            CIRCLE_POS[(x_val, y_val)] = [circle_x_coordinate, circle_y_coordinate]

    board = init_game(bsize)
    display_refresh(board, screen)

    while 1:
        event_loop(board)
        display_refresh(board, screen)

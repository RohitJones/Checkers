from . import utils
from . import color
from . import board
from . import piece

from sys import exit

import pygame


class Player:
    def __init__(self, pid, pcolor, direction):
        self.id = pid
        self.direction = direction
        self.color = pcolor
        self.score = 0
        self.pieces = []

    def get_possible_moves(self, game_state):
        possible_moves = []

        for each_piece in self.pieces:
            possible_moves += list(each_piece.possible_moves(game_state).items())

        kill_moves = [each for each in possible_moves if each[1] is not None]

        if kill_moves:
            return kill_moves

        return possible_moves

    def gpm(self, game_state):
        return [move[0] for move in self.get_possible_moves(game_state)]

    def __repr__(self):
        return "Player: ID:{} | {} ".format(self.id, self.direction)


class Checkers:
    def __init__(self, size, AI=False, difficulty=None, king_exists=False):
        self.size = size
        self.game_board = None
        self.player_1 = Player(1, color.RED, 'up')
        self.player_2 = Player(2, color.BLUE, 'down')
        self.turn = self.player_1
        self.not_turn = self.player_2
        self.selected_piece = None
        self.king_exists = king_exists

        self.screen = None

        self.rect_pos = {}
        self.circle_pos = {}

        for y_val in range(size):
            for x_val in range(size):
                y_coordinate = ((2 * (y_val + 1)) + (100 * y_val))
                x_coordinate = ((2 * (x_val + 1)) + (100 * x_val))
                self.rect_pos[(x_val, y_val)] = [x_coordinate, y_coordinate]

                circle_y_coordinate = (2 * (y_val + 1)) + (100 * y_val) + 100 // 2
                circle_x_coordinate = (2 * (x_val + 1)) + (100 * x_val) + 100 // 2
                self.circle_pos[(x_val, y_val)] = [circle_x_coordinate, circle_y_coordinate]

    def init_game(self):
        pygame.init()

        resolution = (self.size * 100 + (self.size + 1) * 2, self.size * 100 + (self.size + 1) * 2)
        self.screen = pygame.display.set_mode(resolution)

        king = pygame.image.load('Game/res/king.png').convert_alpha()
        self.game_board = board.Board(size=self.size, king=king)

        # Row Col system
        ai_positions = [(0, 1), (0, 3), (0, 5), (1, 0), (1, 2), (1, 4)]
        human_positions = [(4, 1), (4, 3), (4, 5), (5, 0), (5, 2), (5, 4)]

        for index, row_col in enumerate(ai_positions):
            row, col = row_col
            game_piece = piece.Piece('AI' + str(index), (row, col), self.player_2.color, self.player_2.direction)
            self.game_board.state[row][col] = game_piece
            self.player_2.pieces.append(game_piece)

        for index, row_col in enumerate(human_positions):
            row, col = row_col
            game_piece = piece.Piece('HU' + str(index), (row, col), self.player_1.color, self.player_1.direction)
            self.game_board.state[row][col] = game_piece
            self.player_1.pieces.append(game_piece)

    def display_refresh(self):
        self.screen.fill(color.BLACK)
        self.game_board.render(self.screen, self.rect_pos, self.circle_pos)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def game_over(self):
        if len(self.player_2.pieces) == 0 or \
                (self.turn == self.player_2 and not len(self.player_2.get_possible_moves(self.game_board))):
            # message('p1 win')
            return self.player_1

        elif len(self.player_1.pieces) == 0 or \
                (self.turn == self.player_1 and not len(self.player_1.get_possible_moves(self.game_board))):
            # message('p2 win')
            return self.player_2

        else:
            return False

    def start(self):
        self.display_refresh()

        while not self.game_over():
            self.event_loop()
            self.display_refresh()

        print('exited')

    def event_loop(self):
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:

                x, y = pygame.mouse.get_pos()
                row, col = utils.get_clicked_tile(x, y, self.rect_pos, self.size)

                if row == col < 0:
                    continue

                if self.game_board.state[row][col]:
                    # Selecting a piece on the board
                    if self.selected_piece != self.game_board.state[row][col]:
                        self.game_board.cboard = utils.generate_checker_board(self.size)
                        # prevent player from selecting not his piece
                        if self.game_board.state[row][col].color != self.turn.color:
                            self.selected_piece = None
                            continue
                        self.selected_piece = self.game_board.state[row][col]

                    # Highlight possible moves
                    if self.selected_piece:
                        for each_move in self.selected_piece.possible_moves(self.game_board):
                            if each_move in self.turn.gpm(self.game_board):
                                (row, col) = each_move
                                self.game_board.cboard[row][col] = 2

                elif \
                        self.selected_piece and self.selected_piece.color == self.turn.color and \
                        (row, col) in self.turn.gpm(self.game_board) and \
                        (row, col) in self.selected_piece.possible_moves(self.game_board):

                    prev_row, prev_col = self.selected_piece.position
                    self.game_board.state[prev_row][prev_col] = None

                    if self.selected_piece.possible_moves(self.game_board)[(row, col)]:
                        capture_row, capture_col = self.selected_piece.possible_moves(self.game_board)[(row, col)]
                        captured_piece = self.game_board.state[capture_row][capture_col]

                        self.turn.score += 5 if captured_piece.king else 1

                        self.not_turn.pieces.remove(captured_piece)
                        self.game_board.state[capture_row][capture_col].position = None
                        self.game_board.state[capture_row][capture_col] = None

                    self.selected_piece.position = (row, col)
                    self.game_board.state[row][col] = self.selected_piece

                    # promotion to king
                    if \
                            self.king_exists and \
                            ((self.selected_piece.direction == 'up' and row == 0) or
                            (self.selected_piece.direction == 'down' and row == self.size - 1)):

                        self.selected_piece.king = True

                    self.selected_piece = None
                    self.game_board.cboard = utils.generate_checker_board(self.size)
                    self.turn, self.not_turn = self.not_turn, self.turn

                else:
                    self.game_board.selected_piece = None
                    self.game_board.cboard = utils.generate_checker_board(self.size)

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exit()

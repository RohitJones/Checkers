from . import utils
from . import color
from . import board
from . import piece
from . import player

from sys import exit
from copy import deepcopy

import pygame


class Checkers:
    def __init__(self, size, king_exists=False, chaining=False, player_1=None, player_2=None, modified_rules=True):
        self.size = size
        self.game_board = None
        self.player_1 = player.Player(1, color.RED, 'up') if not player_1 else player_1
        self.player_2 = player.Player(2, color.BLUE, 'down') if not player_2 else player_2
        self.turn = self.player_1
        self.not_turn = self.player_2
        self.selected_piece = None
        self.game_over_flag = False

        # for ai course
        self.modified_rules = modified_rules
        self.game_over_method = self.game_over if self.modified_rules else self.game_over_v2

        # Extra Stuff
        self.king_exists = king_exists
        self.chaining = chaining
        self.lock_piece = False
        self.capture = False

        # gfx stuff
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

    def get_copy(self):
        new_game = Checkers(
            size=self.size,
            king_exists=self.king_exists,
            chaining=self.chaining,
            player_1=deepcopy(self.player_1),
            player_2=deepcopy(self.player_2),
            modified_rules=self.modified_rules
        )
        new_game.game_board = self.game_board.get_copy()
        new_game.turn = new_game.player_1 if new_game.player_1.id == self.turn.id else new_game.player_2
        new_game.not_turn = new_game.player_1 if new_game.player_1.id != self.turn.id else new_game.player_2

        return new_game

    def init_game(self):
        pygame.init()

        resolution = (self.size * 100 + (self.size + 1) * 2, self.size * 100 + (self.size + 1) * 2)
        self.screen = pygame.display.set_mode(resolution)

        king = pygame.image.load('Game/res/king.png').convert_alpha()
        self.game_board = board.Board(size=self.size, king=king)

        # Row Col system

        # ai_positions = [(0, 1), (0, 3), (0, 5), (1, 0), (1, 2), (1, 4)]
        # human_positions = [(4, 1), (4, 3), (4, 5), (5, 0), (5, 2), (5, 4)]

        ai_positions = [(0, 1), (0, 3)]
        human_positions = [(3, 0), (3, 2)]

        for index, row_col in enumerate(ai_positions):
            row, col = row_col
            game_piece = piece.Piece('AI' + str(index), (row, col), self.player_2.color, self.player_2.direction)
            self.game_board.state[row][col] = game_piece
            self.player_2.pieces['AI' + str(index)] = game_piece

        for index, row_col in enumerate(human_positions):
            row, col = row_col
            game_piece = piece.Piece('HU' + str(index), (row, col), self.player_1.color, self.player_1.direction)
            self.game_board.state[row][col] = game_piece
            self.player_1.pieces['HU' + str(index)] = game_piece

    def display_refresh(self):
        self.screen.fill(color.BLACK)
        self.game_board.render(self.screen, self.rect_pos, self.circle_pos)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def game_over_v2(self):
        if len(self.player_2.pieces) == 0 or \
                (self.turn == self.player_2 and not len(self.player_2.get_legal_pieces_id(self.game_board))):
            # message('p1 win')
            return self.player_1

        elif len(self.player_1.pieces) == 0 or \
                (self.turn == self.player_1 and not len(self.player_1.get_legal_pieces_id(self.game_board))):
            # message('p2 win')
            return self.player_2

        else:
            return False

    def game_over(self):
        p1 = self.player_1.get_legal_pieces_id(self.game_board)
        p2 = self.player_2.get_legal_pieces_id(self.game_board)

        if not len(p1) and not len(p2):
            return 'draw'

        if not self.player_1.pieces:
            return self.player_2.id

        if not self.player_2.pieces:
            return self.player_1.id

        return None

    def start(self):
        self.display_refresh()

        while not self.game_over_flag:
            if not self.turn.ai:
                self.event_loop()
            else:
                self.turn.iterative_deeping_alpha_beta_search(self)
                self.game_over_flag = True if self.game_over_method() else False

            self.display_refresh()

        print('Winner: {}'.format(self.game_over_method()))

    def move(self, destination, player_instance=None, piece_id=None, kill_location=None, piece_instance=None):
        selected_piece = player_instance.pieces[piece_id] if not piece_instance else piece_instance

        current_row, current_col = selected_piece.position
        destination_row, destination_col = destination

        selected_piece.position = destination_row, destination_col

        self.game_board.state[current_row][current_col] = None
        self.game_board.state[destination_row][destination_col] = selected_piece

        if kill_location:
            kill_row, kill_col = kill_location
            killed_piece = self.game_board.state[kill_row][kill_col]
            killed_piece.position = None
            self.game_board.state[kill_row][kill_col] = None
            del self.not_turn.pieces[killed_piece.id]

        # promotion to king
        if \
                self.king_exists and \
                ((self.selected_piece.direction == 'up' and destination_row == 0) or
                 (self.selected_piece.direction == 'down' and destination_row == self.size - 1)):

            self.selected_piece.king = True
            self.capture = False

        if self.chaining and self.selected_piece.kill_moves(self.game_board) and self.capture:
            self.game_board.cboard = utils.generate_checker_board(self.size)
            self.lock_piece = True

        else:
            self.lock_piece = False
            self.selected_piece = None
            self.game_board.cboard = utils.generate_checker_board(self.size)

            # -------------------------------REFACTOR----------------------------
            if not self.modified_rules:
                self.turn, self.not_turn = self.not_turn, self.turn
            else:
                if len(self.not_turn.get_legal_pieces_id(self.game_board)):
                    self.turn, self.not_turn = self.not_turn, self.turn

    def event_loop(self):
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:

                x, y = pygame.mouse.get_pos()
                row, col = utils.get_clicked_tile(x, y, self.rect_pos, self.size)

                self.capture = False
                if row == col < 0:
                    continue

                if self.game_board.state[row][col]:
                    # Selecting a piece on the board
                    if self.selected_piece != self.game_board.state[row][col] and not self.lock_piece:
                        self.game_board.cboard = utils.generate_checker_board(self.size)
                        # prevent player from selecting not his piece
                        if self.game_board.state[row][col].color != self.turn.color:
                            self.selected_piece = None
                            continue

                        self.selected_piece = self.game_board.state[row][col]

                    # Highlight possible moves
                    if self.selected_piece:
                        for each_move in self.selected_piece.possible_moves(self.game_board):
                            if self.selected_piece.id in self.turn.get_legal_pieces_id(self.game_board):
                                (row, col) = each_move
                                self.game_board.cboard[row][col] = 2

                elif \
                        self.selected_piece and self.selected_piece.color == self.turn.color and \
                        self.selected_piece.id in self.turn.get_legal_pieces_id(self.game_board) and \
                        (row, col) in self.turn.get_legal_end_points(self.game_board) and \
                        (row, col) in self.selected_piece.possible_moves(self.game_board):

                    capture_location = None

                    if self.selected_piece.kill_moves(self.game_board):
                        capture_location = self.selected_piece.kill_moves(self.game_board)[(row, col)]
                        self.capture = True

                    self.move((row, col), kill_location=capture_location, piece_instance=self.selected_piece)

                    # Check if this move caused a game over.
                    self.game_over_flag = True if self.game_over_method() else False

                else:
                    self.selected_piece = None
                    self.game_board.cboard = utils.generate_checker_board(self.size)

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exit()

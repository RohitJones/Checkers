from . import utils
from . import color
from . import board
from . import piece

from sys import exit

import pygame


def init_game(size):
    king = pygame.image.load('Game/res/king.png').convert_alpha()
    game_board = board.Board(size=size, king=king)

    # Row Col system
    ai_positions = [(0, 1), (0, 3), (0, 5), (1, 0), (1, 2), (1, 4)]
    human_positions = [(4, 1), (4, 3), (4, 5), (5, 0), (5, 2), (5, 4)]

    for index, row_col in enumerate(ai_positions):
        row, col = row_col
        game_board.state[row][col] = piece.Piece('AI' + str(index), (row, col), color.BLUE, 'down')

    for index, row_col in enumerate(human_positions):
        row, col = row_col
        game_board.state[row][col] = piece.Piece('HU' + str(index), (row, col), color.RED, 'up')

    return game_board


def event_loop(game_board, rp):

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN:

            x, y = pygame.mouse.get_pos()
            row, col = utils.get_clicked_tile(x, y, rp, game_board.size)

            if game_board.state[row][col]:
                # Selecting a piece on the board
                if game_board.selected_piece != game_board.state[row][col]:
                    game_board.cboard = utils.generate_checker_board(game_board.size)
                    game_board.selected_piece = game_board.state[row][col]

                # Highlight possible moves
                for each_move in game_board.selected_piece.possible_moves(game_board):
                    (row, col) = each_move
                    game_board.cboard[row][col] = 2

            elif game_board.selected_piece and (row, col) in game_board.selected_piece.possible_moves(game_board):
                prev_row, prev_col = game_board.selected_piece.position
                game_board.state[prev_row][prev_col] = None

                if game_board.selected_piece.possible_moves(game_board)[(row, col)]:
                    capture_row, capture_col = game_board.selected_piece.possible_moves(game_board)[(row, col)]
                    game_board.state[capture_row][capture_col].position = None
                    game_board.state[capture_row][capture_col] = None

                game_board.selected_piece.position = (row, col)
                game_board.state[row][col] = game_board.selected_piece

                # promotion to king
                if (game_board.selected_piece.direction == 'up' and row == 0) or \
                        (game_board.selected_piece.direction == 'down' and row == game_board.size - 1):
                    game_board.selected_piece.king = True

                game_board.selected_piece = None
                game_board.cboard = utils.generate_checker_board(game_board.size)

            else:
                game_board.selected_piece = None
                game_board.cboard = utils.generate_checker_board(game_board.size)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        if event.type == pygame.QUIT:
            exit()


def start(size=6):

    pygame.init()
    rect_pos = {}
    circle_pos = {}

    resolution = (size * 100 + (size + 1) * 2, size * 100 + (size + 1) * 2)
    screen = pygame.display.set_mode(resolution)

    for y_val in range(size):
        for x_val in range(size):
            y_coordinate = ((2 * (y_val + 1)) + (100 * y_val))
            x_coordinate = ((2 * (x_val + 1)) + (100 * x_val))
            rect_pos[(x_val, y_val)] = [x_coordinate, y_coordinate]

            circle_y_coordinate = (2 * (y_val + 1)) + (100 * y_val) + 100 // 2
            circle_x_coordinate = (2 * (x_val + 1)) + (100 * x_val) + 100 // 2
            circle_pos[(x_val, y_val)] = [circle_x_coordinate, circle_y_coordinate]

    main_board = init_game(size)
    utils.display_refresh(main_board, screen, rect_pos, circle_pos)

    while 1:
        event_loop(main_board, rect_pos)
        utils.display_refresh(main_board, screen, rect_pos, circle_pos)

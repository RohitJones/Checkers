from Game.player import Player

from random import choice
import threading


class AI(Player):
    def __init__(self, pid, color, direction, piece_count):
        Player.__init__(self, pid, color, direction, ai=True)
        self.piece_count = piece_count  # Number of pieces assigned initially
        self.best_move = None           # best move found in current
        self.infinity = 99999           # infinity used in alpha-beta
        self.time_limit = 15            # time limit
        self.starting_depth = 9         # minimum depth to search
        self.depth_limit = 30           # maximum depth to search

        # storage location of statistics for each move
        self.number_of_nodes = 0
        self.number_of_alpha_prunes = 0
        self.number_of_beta_prunes = 0
        self.temp_list = []

    def eval(self, game):
        """Evaluation function. takes a board object and returns a score.
        if -ve, board favors min player.
        if +ve board favors max player"""
        # get player objects of max and min player
        max_player = game.turn if game.turn.id == self.id else game.not_turn
        min_player = game.not_turn if game.not_turn.id != self.id else game.turn

        # get the pieces of max and min players respectively
        max_player_pieces = [piece for piece in max_player.pieces.values()]
        min_player_pieces = [piece for piece in min_player.pieces.values()]

        # get the piece positions of the max and min players respectively
        max_player_positions = [piece.position for piece in max_player_pieces]
        min_player_positions = [piece.position for piece in min_player_pieces]

        # count the number of moveable pieces (excluding capture moves) of max and min player respectively
        max_player_moveable_piece_count = sum([len(each_piece.possible_moves(game.game_board))
                                               for each_piece in max_player_pieces
                                               if not each_piece.kill_moves(game.game_board)])

        min_player_moveable_piece_count = sum([len(each_piece.possible_moves(game.game_board))
                                               for each_piece in min_player_pieces
                                               if not each_piece.kill_moves(game.game_board)])

        # count the number of safe pieces (along edges of board) of max and min player respectively
        edge = game.size - 1
        max_player_safe_pieces = len([1 for x, y in max_player_positions if x in [0, edge] or y in [0, edge]])
        min_player_safe_pieces = len([1 for x, y in min_player_positions if x in [0, edge] or y in [0, edge]])

        # compute the weighted difference of the above heuristics
        value = ((len(max_player.pieces) - len(min_player.pieces)) * 100 +
                 (max_player_safe_pieces - min_player_safe_pieces) * 75 +
                 (max_player_moveable_piece_count - min_player_moveable_piece_count) * 50)

        return value

    def __idabs(self, game, thread_event):
        """iteratively increases the depth limit and calls alpha-beta"""
        depth_level = self.starting_depth  # set the starting depth level.

        # if the time is not up and depth limit is not reached, increase the depth limit by 1 and call alpha-beta
        while not thread_event.isSet() and depth_level < self.depth_limit:
            # store the best move found by alpha beta for the current depth limit
            best_move = self.__alpha_beta_search(game.get_copy(), depth_level, event=thread_event)

            if not thread_event.isSet():
                # if time is up, give up current computations and return the last best move found.
                if best_move == self.best_move:
                    # if the best move found at current depth level is the same as the last depth level, return the move
                    break
                # store the new best move for the increased depth limit
                self.best_move = best_move
                depth_level += 1

        print("Max depth reached: {}".format(depth_level))

    def iterative_deepening_alpha_beta_search(self, game):
        """Wrapper function to manage the time limit."""
        self.best_move = None
        self.number_of_nodes = 0
        self.number_of_alpha_prunes = 0
        self.number_of_beta_prunes = 0

        time_event = threading.Event()  # create a new thread
        ai_thread = threading.Thread(target=self.__idabs, args=(game, time_event, ))  # thread will call __idabs
        ai_thread.start()  # start the thread function
        ai_thread.join(self.time_limit)  # wait for the time limit or the thread returns
        time_event.set()  # send event that time is up
        ai_thread.join()  # end the thread

        if self.best_move:
            # execute the best move found
            game.move(destination=self.best_move[2],
                      player_instance=game.turn,
                      piece_id=self.best_move[1],
                      kill_location=self.best_move[3])
        else:
            # if no move was found in the time limit, execute a random legal move
            pids = self.get_legal_pieces_id(game.game_board)
            if pids:
                pid = choice(pids)
                mov_pos, kill_pos = choice(list(self.pieces[pid].possible_moves(game.game_board).items()))
                game.move(destination=mov_pos, player_instance=game.turn, piece_id=pid, kill_location=kill_pos)
            else:
                game.turn, game.not_turn = game.not_turn, game.turn

        print('number of nodes: {}\n'
              'number of alpha prunes: {}\n'
              'number of beta prunes:  {}\n'.format(self.number_of_nodes,
                                                    self.number_of_alpha_prunes,
                                                    self.number_of_beta_prunes))

    def __alpha_beta_search(self, game, depth=-1, event=None):
        return self.__max_value(game, -self.infinity, self.infinity, depth, event=event)

    def __max_value(self, game, alpha, beta, depth, kill=None, event=None):

        utility_value = self.__terminal_test(game)  # check if current game state is terminal
        if utility_value is not None:
            return utility_value, None, None, None  # if game state is terminal, return the utility value

        if event.isSet() or depth == 0:  # check if time is up or depth limit has been reached
            if not kill:
                return self.eval(game), None, None, None  # if the previous move was not a kill move, evaluate the state

            else:
                # if last move was a kill move,
                # execute all possible trade kills util no more kill moves are possible
                # and then evaluate the board.
                # Designed to mitigate the horizon effect of alpha-beta
                # relevant reading: https://en.wikipedia.org/wiki/Horizon_effect

                self.temp_list = []
                self.__quiescence_search(game)
                return max(self.temp_list), None, None, None

        best_max_piece_id = best_max_end_pt = best_max_kill_pt = None  # best move found by max
        v = -self.infinity

        # iterate over all legal pieces
        for each_piece_id in game.turn.get_legal_pieces_id(game.game_board):
            # for each legal piece, iterate over all it's possible moves
            for each_end_pt, each_kill_pt in game.turn.pieces[each_piece_id].possible_moves(game.game_board).items():
                if event.isSet():  # check if time is up
                    return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

                max_game_copy = game.get_copy()  # copy current game state for a new node
                self.number_of_nodes += 1

                # execute current move in consideration
                max_game_copy.move(destination=each_end_pt,
                                   player_instance=max_game_copy.turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                # find the score of the current move
                current_move_score, _, _, _ = self.__min_value(game=max_game_copy,
                                                               alpha=alpha,
                                                               beta=beta,
                                                               depth=depth - 1,
                                                               kill=each_kill_pt,
                                                               event=event)
                v = max(v, current_move_score)

                if v == current_move_score and v >= alpha:
                    # if the current move score is better than the last one, store the current move
                    best_max_piece_id, best_max_end_pt, best_max_kill_pt = each_piece_id, each_end_pt, each_kill_pt

                if v >= beta:
                    self.number_of_alpha_prunes += 1
                    return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

                alpha = max(alpha, v)

        # return the move score and the move
        return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

    def __min_value(self, game, alpha, beta, depth, kill=None, event=None):

        utility_value = self.__terminal_test(game)  # check if current game state is terminal
        if utility_value is not None:
            return utility_value, None, None, None  # if game state is terminal, return the utility value

        if event.isSet() or depth == 0:  # check if time is up or depth limit has been reached
            if not kill:
                return self.eval(game), None, None, None  # if the previous move was not a kill move, evaluate the state

            else:
                # if last move was a kill move,
                # execute all possible trade kills util no more kill moves are possible
                # and then evaluate the board.
                # Designed to mitigate the horizon effect of alpha-beta
                # relevant reading: https://en.wikipedia.org/wiki/Horizon_effect

                self.temp_list = []
                self.__quiescence_search(game)
                return min(self.temp_list), None, None, None

        best_min_piece_id = best_min_end_pt = best_min_kill_pt = None  # best move found by min
        v = self.infinity

        # iterate over all legal pieces
        for each_piece_id in game.turn.get_legal_pieces_id(game.game_board):
            # for each legal piece, iterate over all it's possible moves
            for each_end_pt, each_kill_pt in game.turn.pieces[each_piece_id].possible_moves(game.game_board).items():
                if event.isSet():  # check if time is up
                    return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

                min_game_copy = game.get_copy()  # copy current game state for a new node
                self.number_of_nodes += 1

                # execute current move in consideration
                min_game_copy.move(destination=each_end_pt,
                                   player_instance=min_game_copy.turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                # find the score of the current move
                current_move_score, _, _, _ = self.__max_value(game=min_game_copy,
                                                               alpha=alpha,
                                                               beta=beta,
                                                               depth=depth - 1,
                                                               kill=each_kill_pt,
                                                               event=event)
                v = min(v, current_move_score)

                if v == current_move_score and v <= beta:
                    # if the current move score is better than the last one, store the current move
                    best_min_piece_id, best_min_end_pt, best_min_kill_pt = each_piece_id, each_end_pt, each_kill_pt

                if v <= alpha:
                    self.number_of_beta_prunes += 1
                    return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

                beta = min(beta, v)

        # return the move score and the move
        return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

    def __quiescence_search(self, game):
        # Quiescence search is an algorithm typically used to evaluate minimax game trees in
        # game-playing computer programs. It is a remedy for the horizon problem faced by AI engines for various games
        # Source: https://en.wikipedia.org/wiki/Quiescence_search

        if game.turn.killable_count(game.game_board) > 0:
            for each_pid in game.turn.get_legal_pieces_id(game.game_board):
                for each_ept, each_kpt in game.turn.pieces[each_pid].possible_moves(game.game_board).items():
                    qscopy = game.get_copy()
                    self.number_of_nodes += 1
                    qscopy.move(each_ept, qscopy.turn, each_pid, each_kpt)
                    self.__quiescence_search(qscopy)
        else:
            self.temp_list.append(self.eval(game))

    def __terminal_test(self, game):
        """Returns -infinity if min player wins. +infinity if max player wins. 0 if draw"""
        game_over_status = game.game_over()

        if not game_over_status:
            return None

        elif game_over_status == self.id:
            return self.infinity

        elif game_over_status == 'draw':
            return 0

        else:
            return -self.infinity

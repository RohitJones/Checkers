from Game.player import Player

from random import choice
import threading


class AI(Player):
    def __init__(self, pid, color, direction, piece_count, time_limit=15, starting_depth=5):
        Player.__init__(self, pid, color, direction, ai=True)
        self.piece_count = piece_count  # Number of pieces assigned initially
        self.best_move = None           # best move found in current iteration
        self.infinity = 99999           # infinity used in alpha-beta
        self.time_limit = time_limit
        self.starting_depth = starting_depth
        self.depth_limit = 6
        # storage location of statistics for each move
        self.number_of_nodes = 0
        self.number_of_alpha_prunes = 0
        self.number_of_beta_prunes = 0
        self.temp_list = []

    def eval(self, game):
        # """Evaluation method that returns an integer value. value returned is -ve if player is 'min'."""

        # distance_score = 0  # Heuristic that determines how far
        #
        # for each_piece_id in game.turn.pieces:
        #     row, col = game.turn.pieces[each_piece_id].position
        #     if game.turn.pieces[each_piece_id].direction == 'down':
        #         if row == 5:
        #             distance_score += 1200
        #         else:
        #             distance_score += row * 100
        #     else:
        #         if row == 0:
        #             distance_score += 1200
        #         else:
        #             distance_score += (5-row) * 100

        # turn_count = len(game.turn.pieces)
        # not_turn_count = len(game.not_turn.pieces)

        # f1 = (len(game.turn.pieces) - len(game.not_turn.pieces)) * 1000
        # f2 = game.turn.killable_count(game.game_board) * 2000
        # f3 = game.not_turn.killable_count(game.game_board) * 2000

        # f1 = len(game.turn.pieces) - len(game.not_turn.pieces)# * 250
        # # f2 = game.turn.killable_count(game.game_board)*200
        # # f3 = game.not_turn.killable_count(game.game_board) * -800
        #
        # f1 = len(game.turn.pieces) * 115 - (len(game.not_turn.pieces) * 85)
        # f2 = game.turn.killable_count(game.game_board)*50
        # f3 = game.not_turn.killable_count(game.game_board) * -500
        #
        # f1 = (turn_count * 10 + (self.piece_count - not_turn_count) * 7)
        # f2 = game.turn.killable_count(game.game_board)*100
        # f3 = game.not_turn.killable_count(game.game_board)* -10
        #
        # f1 = turn_count * 27 + (self.piece_count - not_turn_count) * 100
        # f2 = game.turn.killable_count(game.game_board)*50
        # f3 = game.not_turn.killable_count(game.game_board) * -150

        # value = f1 + f2 + f3
        max_player = game.turn if game.turn.id == self.id else game.not_turn
        min_player = game.not_turn if game.not_turn.id != self.id else game.turn

        value = len(max_player.pieces) - len(min_player.pieces)

        # if player == 'min':
        #     value = -value

        return value

    def __idabs(self, game, thread_event):
        depth_level = self.starting_depth

        while not thread_event.isSet() and depth_level < self.depth_limit:
            best_move = self.__alpha_beta_search(game.get_copy(), depth_level, event=thread_event)

            if not thread_event.isSet():
                self.best_move = best_move
                depth_level += 1

        print(depth_level)

    def iterative_deepening_alpha_beta_search(self, game):
        self.best_move = None
        self.number_of_nodes = 0
        self.number_of_alpha_prunes = 0
        self.number_of_beta_prunes = 0

        time_event = threading.Event()
        ai_thread = threading.Thread(target=self.__idabs, args=(game, time_event, ))
        ai_thread.start()
        ai_thread.join(self.time_limit)
        time_event.set()
        ai_thread.join()

        if self.best_move:
            game.move(destination=self.best_move[2],
                      player_instance=game.turn,
                      piece_id=self.best_move[1],
                      kill_location=self.best_move[3])
        else:
            print('no move')
            pids = self.get_legal_pieces_id(game.game_board)
            if pids:
                pid = choice(pids)
                mov_pos, kill_pos = choice(list(self.pieces[pid].possible_moves(game.game_board).items()))
                game.move(destination=mov_pos, player_instance=game.turn, piece_id=pid, kill_location=kill_pos)
            else:
                game.turn, game.not_turn = game.not_turn, game.turn

        print('number of nodes: {}\n'
              'number of alpha prunes: {}\n'
              'number of beta prunes:  {}'.format(self.number_of_nodes,
                                                  self.number_of_alpha_prunes,
                                                  self.number_of_beta_prunes))

    def __alpha_beta_search(self, game, depth=-1, event=None):
        return self.__max_value(game, -self.infinity, self.infinity, depth, event=event)

    def __max_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None, event=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if event.isSet() or depth == 0:
            if not prev_killpt:
                return self.eval(game), None, None, None
            else:
                self.temp_list = []
                self.__quiescence_search(game)
                return max(self.temp_list), None, None, None

        best_max_piece_id = best_max_end_pt = best_max_kill_pt = None
        v = -self.infinity

        for each_piece_id in game.turn.get_legal_pieces_id(game.game_board):
            for each_end_pt, each_kill_pt in game.turn.pieces[each_piece_id].possible_moves(game.game_board).items():
                if event.isSet():
                    return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

                max_game_copy = game.get_copy()
                self.number_of_nodes += 1

                max_game_copy.move(destination=each_end_pt,
                                   player_instance=max_game_copy.turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__min_value(max_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt, event=event)
                v = max(v, current_move_score)

                if v == current_move_score and v >= alpha:
                    best_max_piece_id, best_max_end_pt, best_max_kill_pt = current_move

                if v >= beta:
                    self.number_of_alpha_prunes += 1
                    return [v] + current_move

                alpha = max(alpha, v)

        return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

    def __min_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None, event=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if event.isSet() or depth == 0:
            if not prev_killpt:
                return self.eval(game), None, None, None
            else:
                self.temp_list = []
                self.__quiescence_search(game)
                return min(self.temp_list), None, None, None

        best_min_piece_id = best_min_end_pt = best_min_kill_pt = None
        v = self.infinity

        for each_piece_id in game.turn.get_legal_pieces_id(game.game_board):
            for each_end_pt, each_kill_pt in game.turn.pieces[each_piece_id].possible_moves(game.game_board).items():
                if event.isSet():
                    return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

                min_game_copy = game.get_copy()
                self.number_of_nodes += 1

                min_game_copy.move(destination=each_end_pt,
                                   player_instance=min_game_copy.turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__max_value(min_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt, event=event)
                v = min(v, current_move_score)

                if v == current_move_score and v <= beta:
                    best_min_piece_id, best_min_end_pt, best_min_kill_pt = current_move

                if v <= alpha:
                    self.number_of_beta_prunes += 1
                    return [v] + current_move

                beta = min(beta, v)

        return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

    def __quiescence_search(self, game):
        if game.turn.killable_count(game.game_board) > 0:
            for each_pid in game.turn.get_legal_pieces_id(game.game_board):
                for each_ept, each_kpt in game.turn.pieces[each_pid].possible_moves(game.game_board).items():
                    qscopy = game.get_copy()
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

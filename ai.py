from Game.player import Player
from copy import deepcopy
import time


class AI(Player):
    def __init__(self, pid, color, direction, piece_count):
        Player.__init__(self, pid, color, direction, ai=True)
        self.piece_count = piece_count
        self.best_move = None

    def eval(self, game, player):
        max_count = len(game.turn.pieces)
        min_count = len(game.not_turn.pieces)

        if player == 'max':
            return max_count * 7 + (self.piece_count - min_count) * 10
        else:
            return -min_count * 7 - (self.piece_count - max_count) * 10

    def iterative_deeping_alpha_beta_search(self, game):
        self.best_move = None
        start_time = time.time()
        depth_level = 3

        while (time.time() - start_time) < 14.5:
            _game = deepcopy(game)
            score, pid, endpt, killpt = self.__alpha_beta_search(_game, depth_level)
            if self.best_move[0] < score:
                self.best_move = (score, pid, endpt, killpt)

        print(self.best_move)
        game.move(destination=self.best_move[2],
                  player_instance=game.turn,
                  piece_id=self.best_move[1],
                  kill_location=self.best_move[3])

    def __alpha_beta_search(self, game, depth=-1):
        score, pid, endpt, killpt = self.__max_value(game, -99, 99, depth)

        return score

    def __max_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if depth == 0:
            return self.eval(game, 'max'), prev_pid, prev_endpt, prev_killpt

        best_max_piece_id = None
        best_max_end_pt = None
        best_max_kill_pt = None
        v = -99

        max_player = game.turn if game.turn.id == self.id else game.not_turn

        for each_piece_id in max_player.get_legal_pieces_id(game.game_board):
            for each_end_pt, each_kill_pt in max_player.pieces[each_piece_id].possible_moves(game.game_board).items():
                max_game_copy = deepcopy(game)

                max_game_copy.move(destination=each_end_pt,
                                   player_instance=max_player,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__min_value(max_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt)
                v = max(v, current_move_score)

                if v == current_move_score:
                    best_max_piece_id, best_max_end_pt, best_max_kill_pt = current_move

                if v >= beta:
                    return [v] + current_move

                alpha = max(alpha, v)

        return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

    def __min_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if depth == 0:
            return self.eval(game, 'min'), prev_pid, prev_endpt, prev_killpt

        best_min_piece_id = None
        best_min_end_pt = None
        best_min_kill_pt = None
        v = 99

        min_player = game.turn if game.turn.id != self.id else game.not_turn

        for each_piece_id in min_player.get_legal_pieces_id(game.game_board):
            for each_end_pt, each_kill_pt in min_player.pieces[each_piece_id].possible_moves(game.game_board).items():
                min_game_copy = deepcopy(game)

                min_game_copy.move(destination=each_end_pt,
                                   player_instance=min_player,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__max_value(min_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt)
                v = min(v, current_move_score)

                if v == current_move_score:
                    best_min_piece_id, best_min_end_pt, best_min_kill_pt = current_move

                if v <= alpha:
                    return [v] + current_move

                beta = min(beta, v)

        return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

    def __terminal_test(self, game):
        game_over_status = game.game_over()

        if not game_over_status:
            return None

        elif game_over_status == self.id:
            return 99

        elif game_over_status == 'draw':
            p1_count = len(game.turn.pieces)
            p2_count = len(game.not_turn.pieces)

            if p1_count == p2_count:
                return 0

            elif p1_count > p2_count:
                return p1_count*7 + (self.piece_count - p2_count) * 10

            else:
                return -p2_count*7 - (self.piece_count - p1_count) * 10

        else:
            return -99

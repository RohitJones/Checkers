from Game.player import Player

from random import choice
import threading


class AI(Player):
    def __init__(self, pid, color, direction, piece_count):
        Player.__init__(self, pid, color, direction, ai=True)
        self.piece_count = piece_count
        self.best_move = None
        self.infinity = 750 # 99999

    def eval(self, game, player):
        turn_count = len(game.turn.pieces)
        not_turn_count = len(game.not_turn.pieces)

        f1 = turn_count * 100 + (self.piece_count - not_turn_count) * 70
        f2 = game.turn.killable_count(game.game_board)*50
        f3 = game.not_turn.killable_count(game.game_board) * -100

        # f1 = (turn_count * 10 + (self.piece_count - not_turn_count) * 7)
        # f2 = game.turn.killable_count(game.game_board)*100
        # f3 = game.not_turn.killable_count(game.game_board)* -10

        # f1 = turn_count * 27 + (self.piece_count - not_turn_count) * 100
        # f2 = game.turn.killable_count(game.game_board)*63
        # f3 = game.not_turn.killable_count(game.game_board) * -10

        value = f1 + f2 + f3
        if player == 'min':
            value = -value

        # print("{} | {} | {}".format(game.turn, player, value))
        return value

    def __idabs(self, game, thread_event):
        depth_level = 3

        while not thread_event.isSet() and depth_level < 40:
            _game = game.get_copy()
            t = self.__alpha_beta_search(_game, depth_level, event=thread_event)
            score, pid, endpt, killpt = t
            if self.best_move and self.best_move[0] < score:
                self.best_move = (score, pid, endpt, killpt)
            elif not self.best_move:
                self.best_move = (score, pid, endpt, killpt)
            depth_level += 1

        print(depth_level)

    def iterative_deeping_alpha_beta_search(self, game):
        self.best_move = None

        e = threading.Event()
        t = threading.Thread(target=self.__idabs, args=(game, e, ))
        t.start()
        t.join(2)
        e.set()
        t.join()

        if self.best_move:
            game.move(destination=self.best_move[2],
                      player_instance=game.turn,
                      piece_id=self.best_move[1],
                      kill_location=self.best_move[3])
        else:
            pids = self.get_legal_pieces_id(game.game_board)
            if pids:
                pid = choice(pids)
                randmov = choice(self.pieces[pid].possible_moves(game.game_board).items())
                mov_pos, kill_pos = randmov
                game.move(destination=mov_pos, player_instance=game.turn, piece_id=pid, kill_location=kill_pos)
            else:
                game.turn, game.not_turn = game.not_turn, game.turn

        print(self.best_move)
        # game.move(destination=self.best_move[2],
        #           player_instance=game.turn,
        #           piece_id=self.best_move[1],
        #           kill_location=self.best_move[3])

    def __alpha_beta_search(self, game, depth=-1, event=None):
        score, pid, endpt, killpt = self.__max_value(game, -self.infinity, self.infinity, depth, event=event)

        return score, pid, endpt, killpt

    def __max_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None, event=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if event.isSet() or depth == 0:
            return self.eval(game, 'max'), prev_pid, prev_endpt, prev_killpt

        best_max_piece_id = None
        best_max_end_pt = None
        best_max_kill_pt = None
        v = -self.infinity

        max_player = game.turn if game.turn.id == self.id else game.not_turn
        maxt1 = max_player.get_legal_pieces_id(game.game_board)
        for each_piece_id in maxt1:
            maxt2 = max_player.pieces[each_piece_id].possible_moves(game.game_board).items()
            for each_end_pt, each_kill_pt in maxt2:

                if event.isSet():
                    return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

                max_game_copy = game.get_copy()

                max_game_copy.move(destination=each_end_pt,
                                   player_instance=max_game_copy.turn if max_game_copy.turn.id == self.id else max_game_copy.not_turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__min_value(max_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt, event=event)
                v = max(v, current_move_score)

                if v == current_move_score and v >= alpha:
                    best_max_piece_id, best_max_end_pt, best_max_kill_pt = current_move

                if v >= beta:
                    return [v] + current_move

                alpha = max(alpha, v)

        return v, best_max_piece_id, best_max_end_pt, best_max_kill_pt

    def __min_value(self, game, alpha, beta, depth, prev_pid=None, prev_endpt=None, prev_killpt=None, event=None):

        utility_value = self.__terminal_test(game)
        if utility_value is not None:
            return utility_value, prev_pid, prev_endpt, prev_killpt

        if event.isSet() or depth == 0:
            return self.eval(game, 'min'), prev_pid, prev_endpt, prev_killpt

        best_min_piece_id = None
        best_min_end_pt = None
        best_min_kill_pt = None
        v = self.infinity

        min_player = game.turn if game.turn.id != self.id else game.not_turn

        mint1 = min_player.get_legal_pieces_id(game.game_board)
        for each_piece_id in mint1:
            mint2 = min_player.pieces[each_piece_id].possible_moves(game.game_board).items()
            for each_end_pt, each_kill_pt in mint2:

                if event.isSet():
                    return v, best_min_piece_id, best_min_end_pt, best_min_kill_pt

                min_game_copy = game.get_copy()

                min_game_copy.move(destination=each_end_pt,
                                   player_instance=min_game_copy.turn if min_game_copy.turn.id != self.id else min_game_copy.not_turn,
                                   piece_id=each_piece_id,
                                   kill_location=each_kill_pt)

                current_move = [each_piece_id, each_end_pt, each_kill_pt]
                current_move_score, _, _, _ = self.__max_value(min_game_copy, alpha, beta, depth - 1, each_piece_id, each_end_pt, each_kill_pt, event=event)
                v = min(v, current_move_score)

                if v == current_move_score and v <= beta:
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
            return self.infinity

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
            return -self.infinity

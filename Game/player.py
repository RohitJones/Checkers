class Player:
    def __init__(self, pid, pcolor, direction, ai=False):
        self.id = pid
        self.direction = direction
        self.color = pcolor
        self.score = 0
        self.pieces = {}
        self.ai = ai

    def get_legal_pieces_id(self, game_state):
        moveable_pieces = []
        kill_pieces = []

        for each_piece in self.pieces.values():
            if each_piece.possible_moves(game_state):
                moveable_pieces.append(each_piece.id)

            if each_piece.kill_moves(game_state):
                kill_pieces.append(each_piece.id)

        return kill_pieces if kill_pieces else moveable_pieces

    def get_legal_end_points(self, game_state):
        possible_moves = []

        for each_piece in self.pieces.values():
            possible_moves += list(each_piece.possible_moves(game_state).items())

        kill_moves = [each_move for each_move in possible_moves if each_move[1]]

        if kill_moves:
            return [move[0] for move in kill_moves]

        return [move[0] for move in possible_moves]

    def killable_count(self, game_state):
        possible_moves = []

        for each_piece in self.pieces.values():
            possible_moves += list(each_piece.possible_moves(game_state).items())

        return len([each_move for each_move in possible_moves if each_move[1]])

    def __repr__(self):
        return "Player: ID:{} | {} ".format(self.id, self.direction)

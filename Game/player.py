class Player:
    def __init__(self, pid, pcolor, direction, ai=False):
        self.id = pid  # Unique Player ID.
        self.direction = direction  # indicates the direction of travel of the player's pieces.
        self.color = pcolor  # color of the player's pieces.
        self.pieces = {}  # keeps track of all pieces in player's possession. The key is the piece ID
        self.ai = ai  # indicates if a player is an AI

    def get_legal_pieces_id(self, game_state):
        """Returns the piece id of those pieces that are allowed to move.
        If any of the pieces can perform a capture move, only those piece ids are returned"""

        moveable_pieces = []  # stores piece ids of all pieces that can move
        kill_pieces = []  # stores piece ids of all pieces that can perform a capture move

        # iterate over all piece object instances in player's possession
        for each_piece in self.pieces.values():
            # get all possible moves of current piece in consideration
            if each_piece.possible_moves(game_state):
                # if the piece can move, add it to the list of movable pieces.
                moveable_pieces.append(each_piece.id)

            # get all capture moves of current piece in consideration
            if each_piece.kill_moves(game_state):
                # if the piece can kill, add it to the list of kill possible pieces.
                kill_pieces.append(each_piece.id)

        # if even a single piece could perform a kill move, return only those pieces; if not, everything else.
        return kill_pieces if kill_pieces else moveable_pieces

    def get_legal_end_points(self, game_state):
        """Returns the final coordinates, after a move, of all movable pieces in the player's possession"""
        possible_moves = []

        for each_piece in self.pieces.values():
            possible_moves += list(each_piece.possible_moves(game_state).items())

        # get the kill moves, if any.
        kill_moves = [each_move for each_move in possible_moves if each_move[1]]

        # if any kill moves, return only them.
        if kill_moves:
            return [move[0] for move in kill_moves]

        return [move[0] for move in possible_moves]

    def killable_count(self, game_state):
        """Return the number pieces that can be killed given the current state of the board."""
        possible_moves = []

        for each_piece in self.pieces.values():
            possible_moves += list(each_piece.possible_moves(game_state).items())

        return len([each_move for each_move in possible_moves if each_move[1]])

    def __repr__(self):
        return "Player: ID:{} | {} ".format(self.id, self.direction)

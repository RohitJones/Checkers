from Game import Checkers, color
from ai import AI

ai_player2 = AI(2, color.BLUE, 'down', 2)
ai_player1 = AI(1, color.RED, 'up', 2)

game = Checkers(4, player_2=ai_player2)
game.init_game()
game.start()

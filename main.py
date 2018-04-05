from Game import Checkers, color
from ai import AI

ai_player = AI(2, color.BLUE, 'down', 2)

game = Checkers(4, player_2=ai_player)
game.init_game()
game.start()

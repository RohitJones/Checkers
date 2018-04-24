from Game import Checkers, color
from ai import AI

ai_player2 = AI(2, color.BLUE, 'down', 6, 15)
ai_player1 = AI(1, color.RED, 'up', 6, 15)

game = Checkers(6, player_2=ai_player2)
game.init_game()
game.main()
# input('Press enter to continue')
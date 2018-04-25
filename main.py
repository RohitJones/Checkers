from Game import Checkers, color
from ai import AI

difficulty = int(input('Press enter the difficulty (1/2/3):\n1) Easy\n2) Medium\n3) Hard\n'))
first_turn = True if input('Do you want to move first (yes/no)?: ').lower() == 'yes' else False

if difficulty == 1:
    starting_depth = 0
    max_depth = 2
    time_limit = 5

elif difficulty == 2:
    starting_depth = 3
    max_depth = 6
    time_limit = 7

else:
    starting_depth = 9
    max_depth = 30
    time_limit = 15

ai_player = AI(2, color.BLUE, 'down', 6)
ai_player.starting_depth = starting_depth
ai_player.depth_limit = max_depth
ai_player.time_limit = time_limit

game = Checkers(6, player_2=ai_player, first_turn=first_turn)
game.init_game()
game.main()

import locations
import player_p
import board

## Showcasing how to setup a game and how to run it

# Initialize Players and Board
## Player class is for a human player
## AI class is for a human player
##
## For school there are two options "WOLF" and "BEAR" these determine player decks.
## current_position is the starting position for each school, 1 for WOLF and 12 for BEAR. 
P1 = player_p.Player(name='P1',current_position=1,school="WOLF")
P2 = player_p.Player(name='P2',current_position=12,school="BEAR")

AI_1 = player_p.AI(name='AI_BEAR', current_position=12,school="BEAR")
AI_2 = player_p.AI(name='AI_WOLF', current_position=1,school="WOLF")

## Market Definition
market = board.MARKET()

game_map = locations.GameMap()
game_map.start()

##Game map has a graph which we pass into the board class.
board_g = board.Board(graph=game_map.graph, players=[P1,AI_1], market=market)
board_g.start_game(100,True,False)
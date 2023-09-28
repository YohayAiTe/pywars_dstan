import random
from simple_tactical import MyStrategicApi
from tactical_api import distance
import simple_tactical
from simple_tactical import find_closest_piece, builders_moved
import common_types
game_turn = 0


def do_turn(strategic: MyStrategicApi):
    global game_turn
    game_turn += 1


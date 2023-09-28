import common_types
import random
from strategic_api import CommandStatus, StrategicApi, StrategicPiece
from tactical_api import Tank, distance

tank_to_coordinate_to_attack = {}
tank_to_attacking_command = {}
commands = []
builder_next_piece = {}
builder_defending_artillery = {}
real_money = {}
game_turn = 0
builders_targets = {}
builders_moved = {}


def get_sorted_tiles_for_attack(strategic):
    unclaimed_tiles = []
    enemy_tiles = []
    enemy_builder_tiles = []
    for x in range(strategic.get_game_width()):
        for y in range(strategic.get_game_height()):
            coordinate = common_types.Coordinates(x, y)
            danger = strategic.estimate_tile_danger(coordinate)
            if danger == 1:
                unclaimed_tiles.append(coordinate)
            elif danger == 3:
                enemy_builder_tiles.append(coordinate)
            elif danger == 2:
                enemy_tiles.append(coordinate)

    random.shuffle(unclaimed_tiles)
    random.shuffle(enemy_tiles)
    return enemy_builder_tiles, enemy_tiles, unclaimed_tiles



def tanks_attack(strategic, tank_list):
    remaining_tanks = [strategic.context.my_pieces.get(a.id) for a in tank_list]
    enemy_builder_tiles, enemy_tiles, unclaimed_tiles = get_sorted_tiles_for_attack(strategic)
    while len(remaining_tanks) > 0:
        if len (enemy_builder_tiles) > 0:
            coord, tank = find_closest_piece(enemy_builder_tiles, remaining_tanks)
            move_tank_to_destination(tank, coord, check_comid=False, fast_mode=True)
            remaining_tanks.remove(tank)
            enemy_builder_tiles.remove(coord)
            continue
        if len (enemy_tiles) > 0:
            coord, tank = find_closest_piece(enemy_tiles, remaining_tanks)
            move_tank_to_destination(tank, coord, check_comid=False)
            remaining_tanks.remove(tank)
            enemy_tiles.remove(coord)
            continue
        if len (unclaimed_tiles) == 0:
            enemy_builder_tiles, enemy_tiles, unclaimed_tiles = get_sorted_tiles_for_attack(strategic)
            continue
        coord, tank = find_closest_piece(unclaimed_tiles, remaining_tanks)
        move_tank_to_destination(tank, coord, check_comid=False)
        remaining_tanks.remove(tank)
        unclaimed_tiles.remove(coord)

def find_closest_piece (coords_lst, pieces_lst):
    min_dist = 10000
    min_coord = None
    min_piece = None
    for coord in coords_lst:
        for piece in pieces_lst:
            crnt_dist = distance(piece.tile.coordinates, coord)
            if crnt_dist < min_dist:
                min_dist = crnt_dist
                min_piece = piece
                min_coord = coord
    return min_coord, min_piece

def move_piece_to_destination(piece, dest):
    """Returns False if the piece is in destination."""
    piece_coordinate = piece.tile.coordinates

    if random.random() < 0.5:
        if dest.x < piece_coordinate.x:
            new_coordinate = common_types.Coordinates(piece_coordinate.x - 1, piece_coordinate.y)
        elif dest.x > piece_coordinate.x:
            new_coordinate = common_types.Coordinates(piece_coordinate.x + 1, piece_coordinate.y)
        elif dest.y < piece_coordinate.y:
            new_coordinate = common_types.Coordinates(piece_coordinate.x, piece_coordinate.y - 1)
        elif dest.y > piece_coordinate.y:
            new_coordinate = common_types.Coordinates(piece_coordinate.x, piece_coordinate.y + 1)
        else:
            return False
    else:
        if dest.y > piece_coordinate.y:
            new_coordinate = common_types.Coordinates(piece_coordinate.x, piece_coordinate.y + 1)
        elif dest.y < piece_coordinate.y:
            new_coordinate = common_types.Coordinates(piece_coordinate.x, piece_coordinate.y - 1)
        elif dest.x > piece_coordinate.x:
            new_coordinate = common_types.Coordinates(piece_coordinate.x + 1, piece_coordinate.y)
        elif dest.x < piece_coordinate.x:
            new_coordinate = common_types.Coordinates(piece_coordinate.x - 1, piece_coordinate.y)
        else:
            return False
    piece.move(new_coordinate)
    return True


def move_tank_to_destination(tank: Tank, dest, check_comid=True, fast_mode=False):
    """Returns True if the tank's mission is complete."""
    if tank.type != 'tank':
        return
    if check_comid:
        command_id = tank_to_attacking_command[tank.id]
        if dest is None:
            commands[int(command_id)] = CommandStatus.failed(command_id)
            return
    tank_coordinate = tank.tile.coordinates

    is_my = tank.country == tank.tile.country
    if random.random() < 0.5:
        if dest.x < tank_coordinate.x:
            new_coordinate = common_types.Coordinates(tank_coordinate.x - 1, tank_coordinate.y)
        elif dest.x > tank_coordinate.x:
            new_coordinate = common_types.Coordinates(tank_coordinate.x + 1, tank_coordinate.y)
        elif dest.y < tank_coordinate.y:
            new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y - 1)
        elif dest.y > tank_coordinate.y:
            new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y + 1)
        else:
            tank.attack()
            if check_comid:
                commands[int(command_id)] = CommandStatus.success(command_id)
                del tank_to_attacking_command[tank.id]
            return True
    else:
        if dest.y > tank_coordinate.y:
            new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y + 1)
        elif dest.y < tank_coordinate.y:
            new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y - 1)
        elif dest.x > tank_coordinate.x:
            new_coordinate = common_types.Coordinates(tank_coordinate.x + 1, tank_coordinate.y)
        elif dest.x < tank_coordinate.x:
            new_coordinate = common_types.Coordinates(tank_coordinate.x - 1, tank_coordinate.y)
        else:
            tank.attack()
            if check_comid:
                commands[int(command_id)] = CommandStatus.success(command_id)
                del tank_to_attacking_command[tank.id]
            return True
    if is_my or fast_mode:
        tank.move(new_coordinate)
    else:
        tank.attack()
    if check_comid:
        prev_command = commands[int(command_id)]
        commands[int(command_id)] = CommandStatus.in_progress(command_id,
                                                              prev_command.elapsed_turns + 1,
                                                              prev_command.estimated_turns - 1)
    return False



class MyStrategicApi(StrategicApi):
    def __init__(self, *args, **kwargs):
        super(MyStrategicApi, self).__init__(*args, **kwargs)
        global real_money
        real_money = {tile.coordinates: tile.money for tile in self.context.tiles.values()}
        to_remove = set()
        for tank_id, destination in tank_to_coordinate_to_attack.items():
            tank = self.context.my_pieces.get(tank_id)
            if tank is None:
                to_remove.add(tank_id)
                continue
            if move_tank_to_destination(tank, destination):
                to_remove.add(tank_id)
        for tank_id in to_remove:
            del tank_to_coordinate_to_attack[tank_id]
        global builders_moved
        builders_moved = {piece.id: False for piece in self.context.my_pieces.values() if
                    piece.type == "builder"}
        self.find_builders_tragets()

        self.next_turn()

        attacking_pieces = self.report_attacking_pieces()
        tile_index = 0
        tank_list = []
        for piece, command_id in attacking_pieces.items():
            if piece.type != 'tank':
                continue
            tank_list.append(piece)
            # if command_id is not None:
            #    continue
            # strategic.attack(piece, tiles_for_attack[tile_index], 1)
            # tile_index += 1
            # if tile_index >= len(tiles_for_attack):
            #    break
        tanks_attack(self, tank_list)

        # while any(builders_moved.values()):
        #    strategic.find_builders_tragets()
        for piece in self.context.my_pieces.values():
            if piece.type == "builder":
                self.move_builder_to_destination(piece)

    def find_builders_tragets(self):
        builders = [piece for piece in self.context.my_pieces.values() if
                    piece.type == "builder"]
                    #and (
                    #            piece.tile.money == 0 or piece.tile.country != self.context.my_country)]
        good_coords = [tile.coordinates for tile in self.context.tiles.values() if
                       tile.country == self.context.my_country and tile.money and tile.money > 0]
        global builders_targets
        while builders:
            coor, builder = find_closest_piece(good_coords, builders)
            builders_targets[builder.id] = coor
            builders.remove(builder)
            good_coords.remove(coor)
            if not good_coords:
                good_coords = [tile.coordinates for tile in self.context.tiles.values() if
                               tile.country == self.context.my_country and tile.money and tile.money > 0]

    def stop_building_builders_turn(self):
        return 50 if self.context.game_width == 20 else 70 if self.context.game_width == 30 else 20

    def attack(self, piece, destination, radius):
        tank = self.context.my_pieces[piece.id]
        if not tank or tank.type != 'tank':
            return None

        if piece.id in tank_to_attacking_command:
            old_command_id = int(tank_to_attacking_command[piece.id])
            commands[old_command_id] = CommandStatus.failed(old_command_id)

        command_id = str(len(commands))
        attacking_command = CommandStatus.in_progress(command_id, 0, common_types.distance(tank.tile.coordinates, destination))
        tank_to_coordinate_to_attack[piece.id] = destination
        tank_to_attacking_command[piece.id] = command_id
        commands.append(attacking_command)

        return command_id

    def move_builder_to_destination(self, builder):
        """Returns True if the tank's mission is complete."""
        if builder.type != 'builder':
            return
        # if builders_moved[builder.id]:
        #     return
        builders_moved[builder.id] = True
        if builder.id not in builder_next_piece:
            builder_next_piece[builder.id] = 0 if game_turn < self.stop_building_builders_turn() else 1
        if builder_next_piece[builder.id] == 0 and builder.money >= 20:
            builder.build_builder()
            builder_next_piece[builder.id] += 1
            return
        elif builder_next_piece[builder.id] == 1 and builder.money >= 8:
            builder.build_artillery()
            builder_next_piece[builder.id] += 1
        elif builder_next_piece[builder.id] > 1 and builder.money >= 8:
            builder.build_tank()
            builder_next_piece[builder.id] += 1
            return
        artillery = self.context.my_pieces.get(builder_defending_artillery.get(builder.id, None), None)
        if not artillery:
            for piece in self.context.my_pieces.values():
                if piece.type == "artillery" and piece.tile.coordinates == builder.tile.coordinates and piece.id not in builder_defending_artillery.values():
                    builder_defending_artillery[builder.id] = piece.id
                    break
            artillery = self.context.my_pieces.get(builder_defending_artillery.get(builder.id, None), None)
        if not builder_defending_artillery.get(builder.id) and builder_next_piece[builder.id] > 1:
            self.context.log("Whatttttt")

        if real_money[builder.tile.coordinates] > 0 and builder.tile.country == self.context.my_country:
            builder.collect_money(min(builder.tile.money, 5))
            real_money[builder.tile.coordinates] -= 5
            return
        else:
            # locations = [
            #     common_types.Coordinates(builder.tile.coordinates.x - 1, builder.tile.coordinates.y),
            #     common_types.Coordinates(builder.tile.coordinates.x + 1, builder.tile.coordinates.y),
            #     common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y + 1),
            #     common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y - 1)
            # ]
            # locations = list(filter(lambda x: x in self.context.tiles, locations))
            # random.shuffle(locations)
            # for loc in locations:
            #     if real_money[loc] > 0 and self.context.tiles[loc].country == self.context.my_country:
            #         if artillery:
            #             artillery.move(builder.tile.coordinates)
            #             self.context.log(f"{artillery.id} moved in turn {game_turn}")
            #         builder.move(loc)
            #         return
            # for loc in locations:
            #     if self.context.tiles[loc].country == self.context.my_country:
            #         if artillery:
            #             artillery.move(builder.tile.coordinates)
            #         builder.move(loc)
            #         return
            # if artillery:
            #     artillery.move(builder.tile.coordinates)
            # builder.move(random.choice(locations))
            if builder.id in builders_targets:
                move_piece_to_destination(builder, builders_targets[builder.id])
                if artillery:
                    artillery.move(builder.tile.coordinates)
            else:
                builders_moved[builder.id] = False

    def get_piece_by_id(self, piece_id):
        for piece in self.context.all_pieces:
            if piece.id == piece_id:
                return piece
        return None

    def estimate_tile_danger(self, destination):
        tile = self.context.tiles[(destination.x, destination.y)]
        if tile.country == self.context.my_country:
            return 0
        elif tile.country is None:
            return 1
        else:   # Enemy country
            return 2

    def get_game_height(self):
        return self.context.game_height

    def get_game_width(self):
        return self.context.game_width

    def report_attacking_pieces(self):
        return {StrategicPiece(piece_id, piece.type) : tank_to_attacking_command.get(piece_id)
                for piece_id, piece in self.context.my_pieces.items()
                if piece.type == 'tank'}

    def next_turn(self):
        global game_turn
        game_turn += 1
        return game_turn




def get_strategic_implementation(context):
    return MyStrategicApi(context)


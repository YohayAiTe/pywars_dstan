import common_types
from strategic_api import CommandStatus, StrategicApi, StrategicPiece
import tactical_api
import random

tank_to_coordinate_to_attack = {}
tank_to_attacking_command = {}
commands = []
builder_next_piece = {}
builder_defending_artillery = {}
following_unit = {}


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


def move_tank_to_destination(tank, dest):
    """Returns True if the tank's mission is complete."""
    command_id = tank_to_attacking_command[tank.id]
    if dest is None:
        commands[int(command_id)] = CommandStatus.failed(command_id)
        return
    tank_coordinate = tank.tile.coordinates
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
        commands[int(command_id)] = CommandStatus.success(command_id)
        del tank_to_attacking_command[tank.id]
        return True
    tank.move(new_coordinate)
    prev_command = commands[int(command_id)]
    commands[int(command_id)] = CommandStatus.in_progress(command_id,
                                                          prev_command.elapsed_turns + 1,
                                                          prev_command.estimated_turns - 1)
    return False


class MyStrategicApi(StrategicApi):
    def __init__(self, *args, **kwargs):
        super(MyStrategicApi, self).__init__(*args, **kwargs)
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

    def get_piece_by_id(self, piece_id):
        for piece in self.context.all_pieces:
            if piece.id == piece_id:
                return piece
        return None

    def attack(self, piece, destination, radius):
        tank = self.context.my_pieces[piece.id]
        if not tank or tank.type != 'tank':
            return None

        if piece.id in tank_to_attacking_command:
            old_command_id = int(tank_to_attacking_command[piece.id])
            commands[old_command_id] = CommandStatus.failed(old_command_id)

        command_id = str(len(commands))
        attacking_command = CommandStatus.in_progress(command_id, 0,
                                                      common_types.distance(tank.tile.coordinates, destination))
        tank_to_coordinate_to_attack[piece.id] = destination
        tank_to_attacking_command[piece.id] = command_id
        commands.append(attacking_command)

        return command_id

    def move_builder_to_destination(self, builder):
        """Returns True if the tank's mission is complete."""
        if builder.id not in builder_next_piece:
            builder_next_piece[builder.id] = 0
        if builder_next_piece[builder.id] == 0 and builder.money >= 20:
            builder.build_builder()
            builder_next_piece[builder.id] += 1
            return
        if builder_next_piece[builder.id] == 1 and builder.money >= 8:
            builder.build_artillery()
            for piece in self.context.get_sightings(builder.id):
                if piece.type == "artillery" and piece.tile.coordinates == builder.tile.coordinates:
                    builder_defending_artillery[builder.id] = piece.id
                    break
            builder_next_piece[builder.id] += 1
            return
        elif builder_next_piece[builder.id] > 1 and builder.money >= 8:
            builder.build_tank()
            return

        artillery = None
        if builder.id in builder_defending_artillery:
            artillery = self.get_piece_by_id(builder_defending_artillery[builder.id])
            if artillery is None:
                del builder_defending_artillery[builder.id]
        if builder.tile.money > 0 and builder.tile.country == self.context.my_country:
            builder.collect_money(min(builder.tile.money, 5))
        else:
            locations = [
                common_types.Coordinates(builder.tile.coordinates.x - 1, builder.tile.coordinates.y),
                common_types.Coordinates(builder.tile.coordinates.x + 1, builder.tile.coordinates.y),
                common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y + 1),
                common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y - 1)
            ]
            locations = [
                loc for loc in locations
                if loc in self.context.tiles and self.context.tiles[loc].country == self.context.my_country
            ]
            if len(locations) == 0:
                return
            random.shuffle(locations)
            for loc in locations:
                if self.context.tiles[loc].money > 0:
                    if artillery:
                        artillery.move(builder.tile.coordinates)
                    builder.move(loc)
                    return

            if artillery:
                artillery.move(builder.tile.coordinates)
            builder.move(locations[0])

    def closest_of_type(self, coord, piece_type):
        pieces = [piece for piece in self.context.my_pieces.values() if piece.type == piece_type]
        sorted_pieces = sorted(pieces, key=lambda piece: tactical_api.distance(piece.tile.coordinates, coord))
        return sorted_pieces

    def follow_piece(self, following_id, id_to_follow):
        following_unit[following_id] = id_to_follow
        if id_to_follow:
            return move_piece_to_destination(self.context.my_pieces[following_id],
                                             self.context.my_pieces[id_to_follow].tile.coordinates)

    def is_border_tile(self, tile):
        if tile not in self.context.get_tiles_of_country(self.context.my_country):
            return False
        elif self.context.tiles[(tile.coordinates.x + 1, tile.coordinates.y)].country != self.context.my_country or \
                self.context.tiles[(tile.coordinates.x, tile.coordinates.y + 1)].country != self.context.my_country or \
                self.context.tiles[(tile.coordinates.x - 1, tile.coordinates.y)].country != self.context.my_country or \
                self.context.tiles[(tile.coordinates.x, tile.coordinates.y - 1)].country != self.context.my_country:
            return True
        else:
            return False

    def follow_to_random_tile(self, antitank_id):
        my_tiles = self.context.get_tiles_of_country(self.context.my_country)
        border_tiles = [tile for tile in my_tiles if self.is_border_tile(tile)]
        return move_piece_to_destination(antitank_id, random.choice(border_tiles).coordinates)

    def estimate_tile_danger(self, destination):
        tile = self.context.tiles[(destination.x, destination.y)]
        if tile.country == self.context.my_country:
            return 0
        elif tile.country is None:
            return 1
        else:  # Enemy country
            return 2

    def get_game_height(self):
        return self.context.game_height

    def get_game_width(self):
        return self.context.game_width

    def report_attacking_pieces(self):
        return {StrategicPiece(piece_id, piece.type): tank_to_attacking_command.get(piece_id)
                for piece_id, piece in self.context.my_pieces.items()
                if piece.type == 'tank'}


def get_strategic_implementation(context):
    return MyStrategicApi(context)

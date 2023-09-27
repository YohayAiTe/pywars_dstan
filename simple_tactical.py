import common_types
import random
from strategic_api import CommandStatus, StrategicApi, StrategicPiece
from tactical_api import Tank

tank_to_coordinate_to_attack = {}
tank_to_attacking_command = {}
commands = []
builder_next_piece = {}
builder_defending_artillery = {}


def move_tank_to_destination(tank: Tank, dest):
    """Returns True if the tank's mission is complete."""
    if tank.type != 'tank':
        return
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
            commands[int(command_id)] = CommandStatus.success(command_id)
            del tank_to_attacking_command[tank.id]
            return True
    if is_my:
        tank.move(new_coordinate)
    else:
        tank.attack()
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
        if builder.id not in builder_next_piece:
            builder_next_piece[builder.id] = 0
        if builder_next_piece[builder.id] == 0 and builder.money >= 20:
            builder.build_builder()
            builder_next_piece[builder.id] += 1
            return
        elif builder_next_piece[builder.id] == 1 and builder.money >= 8:
            builder.build_artillery()
            for piece in self.context.get_sighings_of_piece(builder.id):
                if piece.type == "artillery" and piece.tile.coordinates == builder.tile.coordinates:
                    builder_defending_artillery[builder.id] = piece.id
                    break
            builder_next_piece[builder.id] += 1
        elif builder_next_piece[builder.id] > 1 and builder.money >= 8:
            builder.build_tank()
            builder_next_piece[builder.id] += 1
            return
        artillery = None
        if builder.id in builder_defending_artillery:
            artillery = self.get_piece_by_id(builder_defending_artillery[builder.id])
            if artillery is None:
                del builder_defending_artillery[builder.id]
        if builder.tile.money > 0 and builder.tile.country == self.context.my_country:
            builder.collect_money(min(builder.tile.money, 5))
            return
        else:
            locations = [
                common_types.Coordinates(builder.tile.coordinates.x - 1, builder.tile.coordinates.y),
                common_types.Coordinates(builder.tile.coordinates.x + 1, builder.tile.coordinates.y),
                common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y + 1),
                common_types.Coordinates(builder.tile.coordinates.x, builder.tile.coordinates.y - 1)
            ]
            locations = list(filter(lambda x: x in self.context.tiles, locations))
            random.shuffle(locations)
            for loc in locations:
                if self.context.tiles[loc].money > 0 and self.context.tiles[loc].country == self.context.my_country:
                    if artillery:
                        artillery.move(builder.tile.coordinates)
                    builder.move(loc)
                    return
            for loc in locations:
                if self.context.tiles[loc].country == self.context.my_country:
                    if artillery:
                        artillery.move(builder.tile.coordinates)
                    builder.move(loc)
                    return
            if artillery:
                artillery.move(builder.tile.coordinates)
            builder.move(random.choice(locations))

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


def get_strategic_implementation(context):
    return MyStrategicApi(context)


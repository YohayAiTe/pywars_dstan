import common_types
from strategic_api import CommandStatus, StrategicApi, StrategicPiece
import random

tank_to_coordinate_to_attack = {}
tank_to_attacking_command = {}
commands = []
builder_next_piece = {}
spy_dest : common_types.Coordinates = None

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
        if builder.id not in builder_next_piece:
            builder_next_piece[builder.id] = 0
        if builder_next_piece[builder.id] == 0 and builder.money >= 20:
            builder.build_builder()
            builder_next_piece[builder.id] += 1
            return
        elif builder_next_piece[builder.id] > 0 and builder.money >= 8:
            builder.build_tank()
            return
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
                    builder.move(loc)
                    return

            builder.move(locations[0])

    def set_spy_destination(self, spy):

        global spy_dest
        my_cord = spy.tile.coordinates
        if self.context.game_height - my_cord.y > my_cord.y:
            spy_dest.y = 2
        else:
            spy_dest.y = self.context.game_height - 2

        if self.context.game_width - my_cord.x > my_cord.x:
            spy_dest.x = 2
        else:
            spy_dest.x = self.context.game_width - 2


    def move_spy_to_destination(self, spy):

        global spy_dest
        sightings = self.context.get_sighings_of_piece(spy.id)
        for sight in sightings:
            for piece in sight.pieces:
                if piece.country != self.context.my_country and piece.type == 'builder':
                    if sight.coordinates != spy.tile.coordinates:
                        spy.move(sight.coordinates)
                    return

        locations = [
            common_types.Coordinates(spy.tile.coordinates.x - 1, spy.tile.coordinates.y),
            common_types.Coordinates(spy.tile.coordinates.x + 1, spy.tile.coordinates.y),
            common_types.Coordinates(spy.tile.coordinates.x, spy.tile.coordinates.y + 1),
            common_types.Coordinates(spy.tile.coordinates.x, spy.tile.coordinates.y - 1)
        ]
        dest = spy_dest
        if dest is not None:
            spy_coordinate = spy.tile.coordinates
            if dest.x < spy_coordinate.x:
                new_coordinate = common_types.Coordinates(spy_coordinate.x - 1, spy_coordinate.y)
            elif dest.x > spy_coordinate.x:
                new_coordinate = common_types.Coordinates(spy_coordinate.x + 1, spy_coordinate.y)
            elif dest.y < spy_coordinate.y:
                new_coordinate = common_types.Coordinates(spy_coordinate.x, spy_coordinate.y - 1)
            elif dest.y > spy_coordinate.y:
                new_coordinate = common_types.Coordinates(spy_coordinate.x, spy_coordinate.y + 1)
            else:
                if spy.country == self.context.my_country:
                    self.set_spy_destination()
                    return
                else:
                    enemy_locations = [
                        loc for loc in locations
                        if self.context.tiles[loc].country == self.context.my_country
                    ]
                    if len(enemy_locations) == 0:
                        random.shuffle(locations)
                        new_coordinate = locations[0]
                    else:
                        money_in_sightings = [
                            sight.money for sight in sightings
                        ]
                        if sum(money_in_sightings) != 0:
                            normalized_money = [m / sum(money_in_sightings) for m in money_in_sightings]
                            choice = random.choices(enemy_locations, normalized_money, k=1)
                            new_coordinate = choice
                        else:
                            random.shuffle(enemy_locations)
                            new_coordinate = enemy_locations[0]
        else:
            random.shuffle(locations)
            new_coordinate = locations[0]

        spy.move(new_coordinate)

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

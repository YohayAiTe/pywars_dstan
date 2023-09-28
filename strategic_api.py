from tactical_api import TurnContext


class StrategicApi(object):
    def __init__(self, context: TurnContext):
        """Constructor. context allows us to use the tactical API."""
        self.context = context

    # ----------------------------------------------------------------------------
    # Attacking military commands.
    # ----------------------------------------------------------------------------

    def attack(self, pieces, destination, radius):
        """Attack the area around the destination, using the given pieces.

        This command should be interepreted as attacking a tile, whose distance of
        `destination` is at most `radius` using the given set of `pieces` (set of
        `StrategicPiece`s).
        This method should return a command identifier.
        """
        raise NotImplementedError()

    def estimate_attack_time(self, pieces, destination, radius):
        """Estimate the amount of required turns for an attack command.

        This method should return an integer, that is the estimated amount of
        turns required for completing an attack command with the given arguments.
        """
        raise NotImplementedError()

    def report_attack_command_status(self, command_id):
        """Given a command identifier, report its status.

        The returned value must be of type `CommandStatus`.
        """
        raise NotImplementedError()

    def report_attacking_pieces(self):
        """Report the current status of all attacking pieces.

        The returned value should be a dict, mapping from StrategicPiece to its
        current command ID that it is executing. Only attacking pieces should be
        included in this report.
        """
        raise NotImplementedError()

    def estimated_required_attacking_pieces(self, destination, radius):
        """Estimates the amount of required pieces for conquering the destination.

        The return value should be an integer.
        """
        raise NotImplementedError()

    def report_missing_intelligence_for_pending_attacks(self):
        """Return all coordinates in which we are missing intelligence.

        Intelligence from the returned tiles would help in improving pending
        attack commands.

        The returned value should be a set of `Coordinates`s.
        """
        raise NotImplementedError()

    def set_intelligence_for_attacks(self, tiles):
        """Provide the implementation with missing intelligence for attacks.

        `tiles` is a `dict` mapping a `Coordinates` object into an `int`,
        representing the danger level of this tile.

        This function does not return any value.
        """
        raise NotImplementedError()

    def report_required_pieces_for_attacks(self):
        """Returns a list of pieces, where they are needed and their priority.

        This method returns a list of tuples, each containing the following values
        (in this order):
        0. Piece type (as `str`).
        1. Destination tile (as `Coordinates`).
        2. Improtance (as `int`).
        """
        raise NotImplementedError()

    def report_required_tiles_for_attacks(self):
        """Returns a list of tiles that are required for completing commands.

        This mehtod returns a list of tuples, each containing the following values
        (in this order):
        0. Tile (as `Coordinates`).
        1. Importance (as `int`).
        """
        raise NotImplementedError()

    def esscort_piece_with_attacking_piece(self, piece, pieces):
        """Esscort the given `piece` with the attacking `pieces`.

        When this command is given, each piece in `pieces` should esscort `piece`.
        `piece` is a `StrategicPiece`, and `pieces` is a `set` of
        `StrategicPiece`s.
        This method should return a command ID.
        """
        raise NotImplementedError()

    # ----------------------------------------------------------------------------
    # Defensive military commands.
    # ----------------------------------------------------------------------------

    def defend(self, pieces, destination, radius):
        """Defend the area around the destination, using the given pieces.

        This command should be interepreted as defending a tile, whose distance of
        `destination` is at most `radius` using the given set of `pieces` (set of
        `StrategicPiece`s).
        This method should return a command identifier.
        """
        raise NotImplementedError()

    def estimate_defend_time(self, pieces, destination, radius):
        """Estimate the amount of required turns form a defense.

        This method should return an integer, that is the estimated amount of
        turns required for forming a defense command with the given arguments.
        """
        raise NotImplementedError()

    def report_defense_command_status(self, command_id):
        """Given a command identifier, report its status.

        The returned value must be of type `CommandStatus`.
        """
        raise NotImplementedError()

    def report_defending_pieces(self):
        """Report the current status of all defending pieces.

        The returned value should be a dict, mapping from StrategicPiece to its
        current command ID that it is executing. Only defending pieces should be
        included in this report.
        """
        raise NotImplementedError()

    def estimated_required_defending_pieces(self, destination, radius):
        """Estimates the amount of required pieces for defending the destination.

        The return value should be an integer.
        """
        raise NotImplementedError()

    def report_missing_intelligence_for_pending_defends(self):
        """Return all coordinates in which we are missing intelligence.

        Intelligence from the returned tiles would help in improving pending
        defend commands.

        The returned value should be a set of `Coordinates`s.
        """
        raise NotImplementedError()

    def set_intelligence_for_defends(self, tiles):
        """Provide the implementation with missing intelligence for defends.

        `tiles` is a `dict` mapping a `Coordinates` object into an `int`,
        representing the danger level of this tile.

        This function does not return any value.
        """
        raise NotImplementedError()

    def report_required_pieces_for_defends(self):
        """Returns a list of pieces, where they are needed and their priority.

        This method returns a list of tuples, each containing the following values
        (in this order):
        0. Piece type (as `str`).
        1. Destination tile (as `Coordinates`).
        2. Improtance (as `int`).
        """
        raise NotImplementedError()

    def report_required_tiles_for_defends(self):
        """Returns a list of tiles that are required for completing commands.

        This mehtod returns a list of tuples, each containing the following values
        (in this order):
        0. Tile (as `Coordinates`).
        1. Importance (as `int`).
        """
        raise NotImplementedError()

    def esscort_piece_with_defending_piece(self, piece, pieces):
        """Esscort the given `piece` with the defending `pieces`.

        When this command is given, each piece in `pieces` should esscort `piece`.
        `piece` is a `StrategicPiece`, and `pieces` is a `set` of
        `StrategicPiece`s.
        This method should return a command ID.
        """
        raise NotImplementedError()

    # ----------------------------------------------------------------------------
    # Intelligence commands.
    # ----------------------------------------------------------------------------

    def estimate_tile_danger(self, destination):
        """Estimate the danger level of the given destination.

        `destination` should be a `Coordinates` object.
        The returned value is an `int`.
        """
        raise NotImplementedError()

    def gather_intelligence(self, pieces, destination, radius):
        """Get intelligence of the area around the destination, using `pieces`.

        This method should return a command identifier.
        """
        raise NotImplementedError()

    def estimate_gathering_time(self, pieces, destination, radius):
        """Estimate the amount of required turns for gathering intelligence.

        This method should return an integer, that is the estimated amount of
        turns required for gathering intelligence command with the given arguments.
        """
        raise NotImplementedError()

    def report_gathering_command_status(self, command_id):
        """Given a command identifier, report its status.

        The returned value must be of type `CommandStatus`.
        """
        raise NotImplementedError()

    def report_intelligence_pieces(self):
        """Report the current status of all intelligence pieces.

        The returned value should be a dict, mapping from StrategicPiece to its
        current command ID that it is executing. Only intelligence pieces should be
        included in this report.
        """
        raise NotImplementedError()

    def report_required_pieces_for_intelligence(self):
        """Returns a list of pieces, where they are needed and their priority.

        This method returns a list of tuples, each containing the following values
        (in this order):
        0. Piece type (as `str`).
        1. Destination tile (as `Coordinates`).
        2. Improtance (as `int`).
        """
        raise NotImplementedError()

    def report_required_tiles_for_intelligence(self):
        """Returns a list of tiles that are required for completing commands.

        This mehtod returns a list of tuples, each containing the following values
        (in this order):
        0. Tile (as `Coordinates`).
        1. Importance (as `int`).
        """
        raise NotImplementedError()

    def esscort_piece_with_intelligence_piece(self, piece, pieces):
        """Esscort the given `piece` with the intelligence `pieces`.

        When this command is given, each piece in `pieces` should esscort `piece`.
        `piece` is a `StrategicPiece`, and `pieces` is a `set` of
        `StrategicPiece`s.
        This method should return a command ID.
        """
        raise NotImplementedError()

    # ----------------------------------------------------------------------------
    # Building commands.
    # ----------------------------------------------------------------------------

    def collect_money(self, builder, amount):
        """Collect a certain amount of money by the given `builder`.

        `builder` should be a `StrategicPiece` object. `amount` should be an `int`.
        This method should return a command ID.
        """
        raise NotImplementedError()

    def estimate_collection_time(self, builder, amount):
        """Estimate the required amount of turns for collecting money.

        This method should return an `int`, that is the estimated amount of turns
        required for collecting the given `amount` of money by the given `builder`.
        """
        raise NotImplementedError()

    def build_piece(self, builder, piece_type):
        """Build a new piece of type `piece_type` using `builder`.

        This methos should be interpreted as "Build a new piece using the given
        `builder`". If the given `builder` does not posses the required amount of
        money for building the required new piece, it should collect it first, and
        then build the new piece.

        `builder` should be a `StrategicPiece` object. `piece_type` is a `str`.
        This method returns a command ID.
        """
        raise NotImplementedError()

    def estimate_building_time(self, builder, piece_type):
        """Estimate the amount of required turns for building a new piece.

        This method should return an integer, that is the estimated amount of
        turns required for building a new piece with the given arguments.
        """
        raise NotImplementedError()

    def report_build_command_status(self, command_id):
        """Given a command identifier, report its status.

        The returned value must be of type `CommandStatus`.
        """
        raise NotImplementedError()

    def get_total_builders_money(self):
        """Returns the total amount of money all the country builders have."""
        raise NotImplementedError()

    def get_total_country_tiles_money(self):
        """Returns the total amount of money the country has on its tiles."""
        raise NotImplementedError()

    def report_builders(self):
        """Report the current status of all builders.

        The returned value should be a `dict`, mapping from a `StrategicPiece`
        objects to a tuple, containing the following values in this order:
        0. The current command ID that this builder is executing, if available, or
           `None` otherwise.
        1. The current amount of money of this builder.
        """
        raise NotImplementedError()

    def report_missing_intelligence_for_collecting_money(self):
        """Return all coordinates in which we are missing intelligence.

        Intelligence from the returned tiles would help in collecting more money.

        The returned value should be a set of `Coordinates`s.
        """
        raise NotImplementedError()

    def set_intelligence_for_builders(self, tiles):
        """Provide the implementation with intelligence for collecting money.

        `tiles` is a `dict` mapping a `Coordinates` object into an `int`,
        representing the danger level of this tile.

        This function does not return any value.
        """
        raise NotImplementedError()

    def report_required_tiles_for_collecting_money(self):
        """Returns a list of tiles that are required for completing commands.

        This mehtod returns a list of tuples, each containing the following values
        (in this order):
        0. Tile (as `Coordinates`).
        1. Importance (as `int`).
        """
        raise NotImplementedError()

    # ----------------------------------------------------------------------------
    # Miscellaneous commands.
    # ----------------------------------------------------------------------------

    def get_my_country(self):
        """Returns the name of this country."""
        raise NotImplementedError()

    def get_all_countries(self):
        """Returns the list of all participating countries in the game."""
        raise NotImplementedError()

    def get_game_width(self):
        """Returns the width of the current game board."""
        raise NotImplementedError()

    def get_game_height(self):
        """Returns the height of the current game board."""
        raise NotImplementedError()

    def log(self, log_entry):
        """Logs the given log entry to the main log of this country.

        log_entry is expected to be a string, without a trailing new line character.
        """
        raise NotImplementedError()

    class CommandStatus(object):
        """Represents the status of a command."""

        @staticmethod
        def failed(command_id):
            """Creates a failed command status."""
            return CommandStatus(command_id, failed=True)

        @staticmethod
        def success(command_id):
            """Creates a successful command status."""
            return CommandStatus(command_id, success=True)

        @staticmethod
        def in_progress(command_id, elapsed_turns, estimated_turns):
            """Create an in-progress command report.

            `elapsed_turns` is the amount of turns since the command has been given.
            `estimated_turns` is the estimated amount of turns required for completing
            the command execution (including `elapsed_turns`).
            """
            return CommandStatus(command_id, elapsed_turns=elapsed_turns, estimated_turns=estimated_turns)

        def __init__(self, command_id, elapsed_turns=None, estimated_turns=None, failed=None, success=None):
            """Constructor.

            Please don't use the constructor directly. Use `CommandStatus.failed`,
            `CommandStstus.success` or `CommandStatus.in_progress` instead.
            """
            self.command_id = command_id
            """The command ID."""
            self.elapsed_turns = elapsed_turns
            """The amount of turns since the command has been given.

            This field is meaningful only if `self.is_in_progress()` returns True.
            """
            self.estimated_turns = estimated_turns
            """The estimated amount of turns required for completing the command execution.

            This field is meaningful only if `self.is_in_progress()` returns True.
            """

            self._failed = failed
            self._success = success

        def is_success(self):
            """Returns True iff this command has succeeded."""
            return self._success == True

        def is_failed(self):
            """Returns True iff this command has failed."""
            return self._failed == True

        def is_in_progress(self):
            """Returns True iff this command is still in progress."""
            return self.elapsed_turns is not None and self.estimated_turns is not None


class CommandStatus(object):
    """Represents the status of a command."""

    @staticmethod
    def failed(command_id):
        """Creates a failed command status."""
        return CommandStatus(command_id, failed=True)

    @staticmethod
    def success(command_id):
        """Creates a successful command status."""
        return CommandStatus(command_id, success=True)

    @staticmethod
    def in_progress(command_id, elapsed_turns, estimated_turns):
        """Create an in-progress command report.

        `elapsed_turns` is the amount of turns since the command has been given.
        `estimated_turns` is the estimated amount of turns required for completing
        the command execution (including `elapsed_turns`).
        """
        return CommandStatus(command_id, elapsed_turns=elapsed_turns, estimated_turns=estimated_turns)

    def __init__(self, command_id, elapsed_turns=None, estimated_turns=None, failed=None, success=None):
        """Constructor.

        Please don't use the constructor directly. Use `CommandStatus.failed`,
        `CommandStstus.success` or `CommandStatus.in_progress` instead.
        """
        self.command_id = command_id
        """The command ID."""
        self.elapsed_turns = elapsed_turns
        """The amount of turns since the command has been given.

        This field is meaningful only if `self.is_in_progress()` returns True.
        """
        self.estimated_turns = estimated_turns
        """The estimated amount of turns required for completing the command execution.

        This field is meaningful only if `self.is_in_progress()` returns True.
        """

        self._failed = failed
        self._success = success

    def is_success(self):
        """Returns True iff this command has succeeded."""
        return self._success == True

    def is_failed(self):
        """Returns True iff this command has failed."""
        return self._failed == True

    def is_in_progress(self):
        """Returns True iff this command is still in progress."""
        return self.elapsed_turns is not None and self.estimated_turns is not None


class StrategicPiece:
    def __init__(self, id, type):
        self.id = id
        self.type = type
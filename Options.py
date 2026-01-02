from dataclasses import dataclass
from Options import Toggle, DefaultOnToggle, Choice, Range, NamedRange, DeathLink, PerGameCommonOptions

class Goal(Range):
    """
    How many lines to clear to win?
    Number of checks will be this x2.5 this amount with tetrominos, x2 with pentominos, more with smaller shape types.
    """
    display_name = "Goal"
    default = 100
    range_start = 1
    range_end = 1000

class StartingShapes(Range):
    """
    Number of shapes to start with
    """
    display_name = "Starting Shapes"
    default = 7
    range_start = 1
    range_end = 100
    
class ExtraShapes(Range):
    """
    Extra shapes to add to the pool to make goaling easier/safer
    """
    display_name = "Extra Shapes"
    default = 20
    range_start = 10
    range_end = 100

class StartingDropMethod(Choice):
    """
    How will shapes fall initially?
    """
    display_name = "Starting Drop Method"
    default = 0
    option_gravity = 0
    option_soft_drop = 1
    option_hard_drop = 2

class RandomizeOrientations(Toggle):
    """
    Randomize the starting orientation of pieces? If disabled, pieces are oriented with flat side down.
    """
    display_name = "Randomize Orientations"

# class StartingBoardHeight(Range):
#     """
#     NOT IMPLEMENTED
#     How tall will the board be when starting? Board height upgrades will become items when not maximum.
#     """
#     display_name = "Starting Board Height"
#     default = 20
#     range_start = 5
#     range_end = 20

class MonominoWeight(NamedRange):
    """
    Ratio of monominos (1-block) to all shape types
    """
    display_name = "Monomino Weight"
    default = 0
    range_start = 0
    range_end = 100
    special_range_names = {
        "none": 0,
        "per unique shapes": 1,
    }

class DominoWeight(NamedRange):
    """
    Ratio of dominos (2-blocks) to all shape types
    """
    display_name = "Domino Weight"
    default = 0
    range_start = 0
    range_end = 100
    special_range_names = {
        "none": 0,
        "per unique shapes": 1,
    }

class TrominoWeight(NamedRange):
    """
    Ratio of tromino (3-blocks) to all shape types
    """
    display_name = "Tromino Weight"
    default = 0
    range_start = 0
    range_end = 100
    special_range_names = {
        "none": 0,
        "per unique shapes": 2,
    }

class TetrominoWeight(NamedRange):
    """
    Ratio of tetromino (4-blocks) to all shape types
    """
    display_name = "Tetromino Weight"
    default = 7
    range_start = 0
    range_end = 100
    special_range_names = {
        "none": 0,
        "per unique shapes": 7,
    }

class PentominoWeight(NamedRange):
    """
    Ratio of pentomino (5-blocks) to all shape types
    """
    display_name = "Pentomino Weight"
    default = 0
    range_start = 0
    range_end = 100
    special_range_names = {
        "none": 0,
        "per unique shapes": 18,
    }

# class TrapItems(Range):
#     """
#     NOT IMPLEMENTED
#     Number of traps present in the world.
#     """
#     display_name = "Traps"
#     default = 0
#     range_start = 0
#     range_end = 100

class NextPieceSlots(Range):
    """
    Number of Next Piece Slots present in the multiworld
    """
    display_name = "Next Piece Slots in Pool"
    default = 5
    range_start = 0
    range_end = 10

class HoldSlots(Range):
    """
    Number of Hold Slots present in the multiworld
    """
    display_name = "Hold Slots in Pool"
    default = 1
    range_start = 0
    range_end = 10

class MaxStackingHeight(Range):
    """
    How high logic expects you to stack blocks to reach tiles.
    Warning! Setting this higher than your board height can make the game more difficult or even impossible!
    """
    display_name = "Max Stacking Height"
    default = 20
    range_start = 0
    range_end = 100

# class SphericalDistribution(Range):
#     """
#     TODO: Delete this completely. It's too jank and not worth it at all.
#     EXPERIMENTAL (Percentage) Make shape distribution sphere-based, making it more likely to get specific shapes as the multiworld progresses?
#     Set to zero to turn off and have pure randomization.
#     """
#     display_name = "Spherical Distribution"
#     default = 0
#     range_start = 0
#     range_end = 80

class DeathOnRestart(Toggle):
    """
    When Death Link is enabled, send a death whenever you reset your board?
    """
    display_name = "Send Death on Restart"

@dataclass
class DracominoOptions(PerGameCommonOptions):
    goal: Goal
    starting_drop_method: StartingDropMethod
    starting_shapes: StartingShapes
    extra_shapes: ExtraShapes
    randomize_orientations: RandomizeOrientations
    # starting_board_height: StartingBoardHeight
    monomino_weight: MonominoWeight
    domino_weight: DominoWeight
    tromino_weight: TrominoWeight
    tetromino_weight: TetrominoWeight
    pentomino_weight: PentominoWeight
    next_piece_slots: NextPieceSlots
    hold_slots: HoldSlots
    max_stacking_height: MaxStackingHeight
    # spherical_distribution: SphericalDistribution
    # trap_items: TrapItems
    death_link: DeathLink
    death_on_restart: DeathOnRestart

dracomino_option_presets = {
    "Classic Tetrominos": {
        "randomize_orientations": False,
        "monomino_weight": 0,
        "domino_weight": 0,
        "tromino_weight": 0,
        "tetromino_weight": 7,
        "pentomino_weight": 0,
    },
    "All Shape Types": {
        "randomize_orientations": True,
        "monomino_weight": 1,
        "domino_weight": 1,
        "tromino_weight": 2,
        "tetromino_weight": 7,
        "pentomino_weight": 18,
    }
}
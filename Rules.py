from typing import Dict, Set, Optional, Callable, List

from BaseClasses import CollectionState
from worlds.generic.Rules import set_rule
from worlds.AutoWorld import World

from .Locations import location_data_table, DracominoLocation
from .Options import DracominoOptions
from .Items import item_data_table
from .ItemPool import DracominoItemPool
from .Constants import BOARD_WIDTH
from . import Util
import math

class DracominoRule:
    event:str
    rule:Callable[[CollectionState], bool]
    optional_rule:Callable[[CollectionState], bool]
    optional_event:Callable[[CollectionState], bool]
    is_progression:bool = True
    is_rule:bool = True
    def __init__(self, event:str, player:int):
        self.event = f"(EVENT) {event}"
        self.optional_event = self.event
        self.rule = lambda state: state.has(self.event, player)
        self.optional_rule = self.rule

def ALWAYS_TRUE(state: CollectionState) -> bool:
    return True

def ALWAYS_FALSE(state: CollectionState) -> bool:
    return False

def combine_rules(*rules: Callable[[CollectionState], bool]) -> Callable[[CollectionState], bool]:
    for v in rules:
        assert callable(v), v
    if len(rules) == 1:
        return rules[0]
    a, b, *r = rules
    if a == ALWAYS_FALSE or b == ALWAYS_FALSE:
        return ALWAYS_FALSE
    if a == ALWAYS_TRUE: return combine_rules(b, *r)
    if b == ALWAYS_TRUE: return combine_rules(a, *r)
    new_rule = lambda state: a(state) and b(state)
    return combine_rules(new_rule, *r)

def either_rule(*rules: Callable[[CollectionState], bool]) -> Callable[[CollectionState], bool]:
    for v in rules:
        assert callable(v), v
    if len(rules) == 1:
        return rules[0]
    a, b, *r = rules
    if a == ALWAYS_TRUE or b == ALWAYS_TRUE:
        return ALWAYS_TRUE
    if a == ALWAYS_FALSE: return either_rule(b, *r)
    if b == ALWAYS_FALSE: return either_rule(a, *r)
    new_rule = lambda state: a(state) or b(state)
    return either_rule(new_rule, *r)

def set_rules(world: World, itempool:DracominoItemPool) -> None:
    multiworld = world.multiworld
    player = world.player
    options:DracominoOptions = world.options

    SHAPES_THAT_CAN_BE_PLACED_IN_CORNER = {shape_name for shape_name in itempool.shapes if not "has_corner_gap" in item_data_table[shape_name].tags}
    SHAPES_THAT_CAN_BE_PLACED_ONE_TILE_FROM_CORNER = {shape_name for shape_name in itempool.shapes if not "has_second_tile_gap" in item_data_table[shape_name].tags}
    SHAPE_TYPES = set(Util.get_shape_weights(options).keys())
    HAS_ONLY_MONOMINOS = len(SHAPE_TYPES.difference({"monomino"})) == 0
    
    def can_rotate(state:CollectionState):
        return state.has_group("Rotate", player)

    def create_shape_value_rule(amount:int) -> Callable[[CollectionState], bool]:
        return lambda state: state.has("Shape Value", player, amount)
    
    def create_poor_height_rule(amount:int) -> Callable[[CollectionState], bool]:
        return lambda state: state.has("Poor Height", player, amount)
    
    def create_safe_height_rule(amount:int) -> Callable[[CollectionState], bool]:
        return lambda state: state.has("Safe Height", player, amount)
    
    def create_item_pickup_rule(amount:int, placement:int) -> Callable[[CollectionState], bool]:
        # TODO: Board Height Upgrades: This rule must be changed when there's board height upgrades
        BOARD_HEIGHT_UPGRADES = 20
        # Having stack height be as high the goal might cause problems with the randomizer resolving fills
        ACTUAL_MAX_STACKING_HEIGHT = min(options.max_stacking_height.value, options.goal.value)
        
        height_limit:int = min(BOARD_HEIGHT_UPGRADES, ACTUAL_MAX_STACKING_HEIGHT)
        location_height = math.floor(placement/BOARD_WIDTH)
        reach_height:int = min(height_limit, location_height)
        SHAPE_VALUE_REDUCTION_WITH_ROTATIONS:int = reach_height*(BOARD_WIDTH - 2)
        SHAPE_VALUE_REDUCTION_WITHOUT_ROTATIONS:int = reach_height*(BOARD_WIDTH - 4)
        
        return either_rule(
            # Rules when we have rotate
            combine_rules(
                ALWAYS_TRUE if HAS_ONLY_MONOMINOS else can_rotate,
                create_shape_value_rule(1 + max(0, amount - SHAPE_VALUE_REDUCTION_WITH_ROTATIONS)),
                create_safe_height_rule(reach_height)
            ),
            # Need line clears to go any higher
            ALWAYS_FALSE if location_height > ACTUAL_MAX_STACKING_HEIGHT
            # Rotate is irrelevant for monominos
            else ALWAYS_FALSE if HAS_ONLY_MONOMINOS
            # Rules for bottom corners and minos with gaps
            else (lambda state: state.has_any(SHAPES_THAT_CAN_BE_PLACED_IN_CORNER, player)) if placement == 1
            else (lambda state: state.has_any(SHAPES_THAT_CAN_BE_PLACED_ONE_TILE_FROM_CORNER, player)) if placement == 2
            else (lambda state: state.has_any(SHAPES_THAT_CAN_BE_PLACED_ONE_TILE_FROM_CORNER, player)) if placement == BOARD_WIDTH - 2
            else (lambda state: state.has_any(SHAPES_THAT_CAN_BE_PLACED_IN_CORNER, player)) if placement == BOARD_WIDTH - 1
            # Rule for everywhere else without rotate
            else combine_rules(
                create_shape_value_rule(1 + max(0, amount - SHAPE_VALUE_REDUCTION_WITHOUT_ROTATIONS)),
                create_poor_height_rule(reach_height)
            )
        )
    
    def create_line_clear_rule(amount:int) -> Callable[[CollectionState], bool]:
        return combine_rules(
            ALWAYS_TRUE if HAS_ONLY_MONOMINOS else can_rotate,
            create_shape_value_rule(amount)
        )

    # Set location rules
    for location in multiworld.get_locations(player):
        if isinstance(location, DracominoLocation):
            location_data = location_data_table[location.name]
            if "line_clear" in location_data.tags:
                set_rule(location, create_line_clear_rule(location.shape_value_to_reach))
            elif "item_pickup" in location_data.tags:
                set_rule(location, create_item_pickup_rule(location.shape_value_to_reach, location.placement))

    # Set the win conditions
    multiworld.completion_condition[player] = create_line_clear_rule((options.goal.value + options.line_clear_leniency.value) * BOARD_WIDTH)
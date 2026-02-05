from typing import Dict, Set, List, Iterable

from worlds.AutoWorld import World, WebWorld
from .Options import DracominoOptions, dracomino_option_presets
from . import Regions, Rules, ItemPool, Util
from .Constants import VERSION, MIN_GAME_VERSION, BOARD_WIDTH
from .Locations import DracominoLocation, location_data_table, location_name_to_id
from .Items import item_data_table, item_name_to_id, item_name_groups, DracominoItem
import math

from BaseClasses import Item, Tutorial, CollectionState

class DracominoWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Tutorial",
        "A guide to setting up the Archipelago Dracomino game.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Dragon Wolf Leo"]
    )]
    options_presets = dracomino_option_presets
    theme = "stone"

class DracominoWorld(World):
    """
    Dracomino is a falling block puzzle game where you place falling shapes to pick up coins on the board
    or arrange into rows to clear them and find items.
    """
    game = "Dracomino"

    item_name_to_id = item_name_to_id
    item_name_groups = item_name_groups
    location_name_to_id = location_name_to_id

    options_dataclass = DracominoOptions
    options: DracominoOptions
    topology_present = False
    web = DracominoWeb()

    dracomino_itempool: ItemPool.DracominoItemPool

    def __init__(self, multiworld, player):
        self.dracomino_itempool = ItemPool.DracominoItemPool()
        super().__init__(multiworld, player)

    def generate_early(self):
        # Check that anything has a weight
        SHAPE_WEIGHTS = Util.get_shape_weights(self.options)
        has_weight = False
        for weight in SHAPE_WEIGHTS.values():
            if weight:
                has_weight = True
                break
        
        # If player didn't set weights, default to tetromino
        if not has_weight:
            self.options.tetromino_weight.value = 1

        # Create itempools
        self.dracomino_itempool.decide_itempools(self)

    def create_item(self, name: str) -> Item:
        return self.dracomino_itempool.create_item(self, name)

    def create_items(self) -> None:
        self.dracomino_itempool.create_items(self)

    def get_filler_item_name(self) -> str:
        return self.dracomino_itempool.get_filler_item_name(self)

    def create_regions(self):
        Regions.create_regions(self.multiworld, self.player, self.options, self.dracomino_itempool)

    def set_rules(self) -> None:
        Rules.set_rules(self, self.dracomino_itempool)

    def collect(self, state: CollectionState, item: Item) -> bool:
        change = super().collect(state, item)
        if change and isinstance(item, DracominoItem) and item.name in item_data_table:
            # Keep track of the number of blocks in state
            state.prog_items[item.player]["Shape Value"] += item_data_table[item.name].shape_value
            state.prog_items[item.player]["Poor Height"] += item_data_table[item.name].poor_height
            state.prog_items[item.player]["Safe Height"] += item_data_table[item.name].safe_height
        return change

    def remove(self, state: CollectionState, item: Item) -> bool:
        change = super().remove(state, item)
        if change and isinstance(item, DracominoItem) and item.name in item_data_table:
            # Keep track of the number of blocks in state
            state.prog_items[item.player]["Shape Value"] -= item_data_table[item.name].shape_value
            state.prog_items[item.player]["Poor Height"] -= item_data_table[item.name].poor_height
            state.prog_items[item.player]["Safe Height"] -= item_data_table[item.name].safe_height
        return change
    
    def extend_hint_information(self, hint_data: Dict[int, Dict[int, str]]):
        # Tell which line each item pickup is on
        hint_information:Dict[int, str] = {}
        for location in self.multiworld.get_locations(self.player):
            if isinstance(location, DracominoLocation):
                if "item_pickup" in location_data_table[location.name].tags:
                    line_num = math.floor(location.placement/BOARD_WIDTH) + 1
                    hint_information[location.address] = f"Line {line_num}"
        hint_data[self.player] = hint_information

    def fill_slot_data(self):
        # Create item placement data
        item_pickup_placements:List[int] = []
        EXISTING_LOCATIONS = {location.name for location in self.multiworld.get_locations(self.player)}
        i = 1
        while f"Coin {i}" in EXISTING_LOCATIONS:
            location = self.get_location(f"Coin {i}")
            if isinstance(location, DracominoLocation):
                item_pickup_placements.append(location.placement)
            else:
                break
            i += 1
        # DEBUG: Check that there's no dupes
        for v in item_pickup_placements:
            # Keep this here a little longer so I can be sure it doesn't happen anymore
            assert item_pickup_placements.count(v) == 1, \
                f"{self.player_name} (Dracomino) Found multiple location placement {v} in slot data; {item_pickup_placements}; Report to dev if seeing this!"
        slot_data = {
            "generator_version":        VERSION,
            "min_game_version":         MIN_GAME_VERSION,
            "death_link":               bool(self.options.death_link.value),
            "death_on_restart":         bool(self.options.death_on_restart.value),
            "goal":                     self.options.goal.value,
            # "starting_board_height":    self.options.starting_board_height.value,
            "item_pickup_placements":   item_pickup_placements,
            "randomize_orientations":   bool(self.options.randomize_orientations.value),
            # Things that will probably only be needed by trackers (added v0.2.1)
            "line_clear_leniency":      self.options.line_clear_leniency.value,
            "max_stacking_height":      self.options.max_stacking_height.value,
        }
        return slot_data
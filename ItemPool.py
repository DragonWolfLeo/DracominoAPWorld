from typing import Dict, List, FrozenSet
from worlds.AutoWorld import World
from BaseClasses import ItemClassification as IC
from .Items import item_data_table, item_name_to_id, DracominoItem
from .Options import DracominoOptions
from .Constants import BOARD_WIDTH
from . import Util

class ShapeGenerator:
    shape_pool:List[str]
    current_bag:List[str]
    def __init__(self, shape_pool:List[str]):
        self.shape_pool = shape_pool
        self.current_bag = self.shape_pool.copy()

    def create(self, world:World) -> str:
        # Refill
        if len(self.current_bag) == 0:
            self.current_bag.extend(self.shape_pool)
        # Pull from the list
        return self.current_bag.pop(world.random.randint(0, len(self.current_bag) - 1))
    
    def reset_bag(self) -> None:
        self.current_bag.clear()
        self.current_bag.extend(self.shape_pool)
    
class DracominoItemPool:
    normal_itempool:List[str] # All items except junk
    shapes:List[str]
    region_order:List[str] 
    location_shape_value_costs:List[int]
    overflow_shape_value:int

    def decide_itempools(self, world:World) -> None:
        "Before generating, decide what items go in itempool categories"
        options:DracominoOptions = world.options
        SHAPE_WEIGHTS = Util.get_shape_weights(options)

        # Set instance variables
        self.normal_itempool = list()
        self.region_order = list()
        self.location_shape_value_costs = list()
        self.shapes:List[str] = list()
        self.overflow_shape_value:int = 0

        #
        trap_items:List[str] = list()

        # Give starting drop ability
        options.start_inventory.value[
                 "Soft Drop" if options.starting_drop_method.value == options.starting_drop_method.option_soft_drop
            else "Hard Drop" if options.starting_drop_method.value == options.starting_drop_method.option_hard_drop
            else "Gravity"
        ] = 1

        start_inventory_as_set:FrozenSet = frozenset(options.start_inventory.value.keys())

        # Build shape whitelist
        whitelisted_shape_types = [shape_type for shape_type, weight in SHAPE_WEIGHTS.items() if weight]
        
        for name, item in item_data_table.items():
            # Progressive items should be handled elsewhere
            if not item.code or "progressive" in item.tags:
                continue
            # Add abilites to the pool
            if "ability" in item.tags and not name in start_inventory_as_set:
                self.normal_itempool.append(name)
                continue
            # Sort other items types into groups
            if "shape" in item.tags and len(item.tags.intersection(whitelisted_shape_types)):
                self.shapes.append(name)
                continue
            if "trap" in item.tags:
                trap_items.append(name)
                continue

        # Make weighted list to pull types from
        shape_type_weighted_list:List[str] = []
        for shape_type in whitelisted_shape_types:
            for _ in range(SHAPE_WEIGHTS[shape_type]):
                shape_type_weighted_list.append(shape_type)

        # Make shape generators to pull from
        shape_generators:Dict[str,ShapeGenerator] = {
            **{
                shape_type: ShapeGenerator([
                    shape_name for shape_name in self.shapes if shape_type in item_data_table[shape_name].tags
                ]) for shape_type in whitelisted_shape_types
            }
        }
        
        # Add starting shapes
        for _ in range(options.starting_shapes.value):
            shape_type = world.random.choice(shape_type_weighted_list)
            shape_name = shape_generators[shape_type].create(world)
            world.multiworld.push_precollected(self.create_item(world, shape_name))
                
        # Calculate number of blocks so we have enough shapes to 
        num_blocks_to_fill:int = options.goal.value*BOARD_WIDTH

        # Subtract blocks that are already in start inventory
        for item in world.multiworld.precollected_items[world.player]:
            if item.name in item_data_table:
               num_blocks_to_fill -= item_data_table[item.name].shape_value

        # Handle progressive items here
        for _ in range(options.next_piece_slots.value):
            self.normal_itempool.append("Next Piece Slot")
        for _ in range(options.hold_slots.value):
            self.normal_itempool.append("Hold Slot")

        # # Create traps
        # for _ in range(options.trap_items.value):
        #     trap_name = world.random.choice(trap_items) if len(trap_items) else "Nothing"
        #     self.normal_itempool.append(trap_name)
        #     # TODO: Any trap with shape value must be progression!
        #     num_blocks_to_fill -= item_data_table[trap_name].shape_value # In case traps add/are blocks

        # Create shapes until there's enough blocks filled plus extra shapes
        num_extra_shapes = options.extra_shapes.value
        while num_blocks_to_fill > 0 or num_extra_shapes > 0:
            shape_type = world.random.choice(shape_type_weighted_list)
            shape_name = shape_generators[shape_type].create(world)
            # Add shape to the pool and subtract its block value
            self.normal_itempool.append(shape_name)
            _shape_value = item_data_table[shape_name].shape_value
            if num_blocks_to_fill > 0:
                num_blocks_to_fill -= _shape_value
            else:
                num_extra_shapes -= 1
            # Add to location shape values
            self.location_shape_value_costs.append(_shape_value)

        # # Create region order
        # if options.spherical_distribution.value > 0:
        #     # Give shapes their own region and shuffle
        #     self.region_order = self.shapes.copy()
        #     world.random.shuffle(self.region_order)

    def create_item(self, world:World, name: str) -> DracominoItem:
        itemtype = (
            item_data_table[name].type if name in item_name_to_id
            else IC.progression
        )
        return DracominoItem(
            name,
            itemtype,
            item_data_table[name].code if name in item_name_to_id else None,
            world.player
        )

    def create_items(self, world: World) -> None:
        item_pool: List[DracominoItem] = []
        items_to_put_in_pool: List[DracominoItem] = []

        # Create the items
        for name in self.normal_itempool:
             # Abilities and stuff should always be in the item pool, while shapes should overflow into start inventory
            (
                items_to_put_in_pool if "shape" in item_data_table[name].tags
                else item_pool
            ).append(self.create_item(world, name))

        unfilled_locations = world.multiworld.get_unfilled_locations(world.player)
        num_total_locations_to_fill = len(unfilled_locations) - len(item_pool)

        # Fill until we run out of locations
        for _ in range(max(num_total_locations_to_fill, 0)):
            if len(items_to_put_in_pool):
                item_pool.append(items_to_put_in_pool.pop())
            else:
                break

        # TODO: I don't think is even possible to get this anymore
        # If we ran out of locations to put things, then remaining items will be added into starting inventory
        if len(items_to_put_in_pool):
            print("Pushing",len(items_to_put_in_pool),"items into start inventory. This is unintended, but shouldn't cause a problem.")
        while len(items_to_put_in_pool):
            item = items_to_put_in_pool.pop()
            world.multiworld.push_precollected(item)
            self.overflow_shape_value += item_data_table[item.name].shape_value

        # TODO: I don't think is even possible to get this anymore
        if len(item_pool) > len(world.multiworld.get_unfilled_locations(world.player)):
            print(f"{world.multiworld.get_player_name(world.player)} (Dracomino): Warning! More items than locations!")

        world.multiworld.itempool += item_pool

    def get_filler_item_name(self, world: World) -> str:
        if len(self.shapes) > 0:
            return world.random.choice(self.shapes)
        return "Nothing"
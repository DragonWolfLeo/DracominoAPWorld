from typing import Dict, List, NamedTuple, Set, Callable, Optional
from BaseClasses import MultiWorld, Region, Entrance, CollectionState
from .Locations import location_data_table, DracominoLocation
from .ItemPool import DracominoItemPool
from .Options import DracominoOptions
from .Constants import BOARD_WIDTH, BOARD_HEIGHT
from . import Util
import math

class DracominoRegionData(NamedTuple):
    connecting_regions: List[str]
    locations: List[str]

def create_regions(multiworld: MultiWorld, player: int, options:DracominoOptions, itempool:DracominoItemPool):
    world = multiworld.worlds[player]
    region_name_list: List[str] = ["Menu"]
    region_data_table: Dict[str, DracominoRegionData] = {
        "Menu": DracominoRegionData([], []),
    }
    
    # Build region table, each connected to the next
    # TODO: Right now there's no extra regions, but keeping this code here in case I do need it??
    for region_name in itempool.region_order:
        region_data_table[region_name] = DracominoRegionData([], [])
        region_name_list.append(region_name)

    for j in range(max(0, len(region_name_list)-1)):
        region_data_table[region_name_list[j]].connecting_regions.append(region_name_list[j+1])

    location_shape_values_to_reach:Dict[str, int] = {}
    location_placements:Dict[str, int] = {}
    def place_locations(location_type:str, total:int, placement_fn:Callable[[int], int]):
        _eligible_locations:List[str] = [name for name, data in location_data_table.items() if location_type in data.tags]
        _eligible_locations.sort(key = (lambda key: location_data_table[key].address), reverse=True)
        _num_regions = len(region_name_list)
        i:int = 0
        while i < total and len(_eligible_locations):
            _region_index = min(
                _num_regions - 1,
                math.floor(
                    _num_regions*i/total
                )
            )
            _location_name = _eligible_locations.pop()
            placement = placement_fn(i)
            location_placements[_location_name] = placement
            location_shape_values_to_reach[_location_name] = placement - (placement % BOARD_WIDTH)
            region_data_table[region_name_list[_region_index]].locations.append(_location_name)
            i += 1

    LINE_GOAL = options.goal.value
    NUM_LINE_LOCATIONS = LINE_GOAL - 1
    # Place line-clear locations
    place_locations("line_clear", NUM_LINE_LOCATIONS, lambda index: (index+1) * BOARD_WIDTH)

    # Calculate location shape value multiplier to spread out item pickups across the height
    def calc_item_pickup_shape_value_multiplier() -> float:
        HEIGHT_LIMIT = min(BOARD_HEIGHT>>1, options.max_stacking_height.value) # Extends placement vertically by half board height
        total_locations = len(itempool.normal_itempool)
        item_pickup_locations = total_locations - NUM_LINE_LOCATIONS

        shape_value_in_item_pickups = 0
        total_shape_value = -itempool.overflow_shape_value # Overflow shape value is part of shape value costs so let's subtract it out
        for i, cost in enumerate(itempool.location_shape_value_costs):
            # The first chunk of location costs is used for item pickups, while the rest is just added to the total in existence
            if i < item_pickup_locations:
                shape_value_in_item_pickups += cost
            total_shape_value += cost

        item_pickup_location_ratio = shape_value_in_item_pickups/total_shape_value
        shape_value_balancer = LINE_GOAL*BOARD_WIDTH/max(1, total_shape_value) # Stretches location distribution to fit goal region
        height_extension_multiplier = (LINE_GOAL + HEIGHT_LIMIT)/LINE_GOAL # Extends the height limit of pickups above the goal line
        return shape_value_balancer * height_extension_multiplier / item_pickup_location_ratio

    # Calculate how far item pickups are
    _SHAPE_VALUE_MULTIPLIER = calc_item_pickup_shape_value_multiplier()
    def item_pickup_shape_value(index:int) -> int:
        value:int = 0
        i:int = 0
        while i < index and i < len(itempool.location_shape_value_costs):
            value += itempool.location_shape_value_costs[i]
            i += 1
        if i < len(itempool.location_shape_value_costs):
            # Randomize the position of each placement
            offset_range:int = itempool.location_shape_value_costs[i]
            value += world.random.randint(0, offset_range-1)
        return math.floor(value*_SHAPE_VALUE_MULTIPLIER)
    
    # Place item-pickup locations
    place_locations("item_pickup", len(itempool.normal_itempool) - NUM_LINE_LOCATIONS, item_pickup_shape_value)

    # Create regions
    for region_name in region_name_list:
        new_region = Region(region_name, player, multiworld)
        multiworld.regions.append(new_region)

    # Create locations and entrances and rules
    for region_name in region_name_list:
        region_data = region_data_table[region_name]
        # Fill the region with locations
        region = world.get_region(region_name)
        region.add_locations({
            location_name: location_data_table[location_name].address for location_name in region_data.locations
        }, DracominoLocation)
        if region_data.connecting_regions:
            for exit_name in region_data.connecting_regions:
                entrance = Entrance(player, f"{region_name} -> {exit_name}", region)
                entrance.connect(world.get_region(exit_name))
                region.exits.append(entrance)

    # Apply shape value distances to locations
    for location in multiworld.get_locations(player):
        if isinstance(location, DracominoLocation):
            location.shape_value_to_reach = location_shape_values_to_reach.get(location.name, 0)
            location.placement = location_placements.get(location.name, 0)
            # print(f"{location.name}: {location.placement}")
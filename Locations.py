from typing import Dict, NamedTuple, Optional, Set

from BaseClasses import Location

from .Constants import LOCATIONS

class DracominoLocation(Location):
    game:str = "Dracomino"
    shape_value_to_reach:int = 0 # To be set by create_regions and used by create_rules
    placement:int = 0

class DracominoLocationData(NamedTuple):
    address: Optional[int] = None
    tags: Set[str] = set()
    name: str = ""

def generate_location_data() -> Dict[str, DracominoLocationData]:
    ret: Dict[str, DracominoLocationData] = {}
    for v in LOCATIONS:
        address:int = v[0]
        name:str = v[1]
        tags:Set = set(v[2])

        ret.setdefault(name, DracominoLocationData(address, tags, name))
    return ret

location_data_table: Dict[str, DracominoLocationData] = generate_location_data()
location_name_to_id = {name: data.address for name, data in location_data_table.items() if data.address is not None}
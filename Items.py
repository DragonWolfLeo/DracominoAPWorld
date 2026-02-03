from typing import Dict, NamedTuple, Optional, Set

from BaseClasses import Item, ItemClassification as IC
from .Constants import ITEMS, SHAPE_VALUES

class DracominoItem(Item):
    game = "Dracomino"

class DracominoItemData(NamedTuple):
    code:Optional[int] = None
    type:IC = IC.filler
    tags:Set[str] = set()
    shape_value:int = 0 # The number of blocks a shape is worth
    poor_height:int = 0 # The "worst case" amount of height a piece is expected to reach, when rotate is not available
    safe_height:int = 0 # A "safe" amount of height a piece is expected to reach, when rotate is available

def generate_item_map() -> Dict[str, DracominoItemData]:
    ret: Dict[str, DracominoItemData] = {}
    ret.setdefault("Nothing", DracominoItemData(None, IC.filler))
    for v in ITEMS:
        code:int = v[0]
        name:str = v[1]
        tags: Set[str] = set(v[2])

        classification:IC = (
            IC.progression if "progression" in tags else
            IC.progression_skip_balancing if "progression_skip_balancing" in tags else
            IC.useful if "useful" in tags else
            IC.trap if "trap" in tags else
            IC.filler
        )

        shape_value:int = 0
        for shape_type, value in SHAPE_VALUES.items():
            if shape_type in tags:
                shape_value = value
                break

        poor_height:int = v[3] if len(v) > 3 else 0
        safe_height:int = v[4] if len(v) > 4 else 0

        if not "deprecated" in tags:
            ret.setdefault(name, DracominoItemData(code, classification, tags, shape_value, poor_height, safe_height))
    return ret

def generate_item_name_groups() -> Dict[str, Set[str]]:
    ret:Dict[str, Set[str]] = {}
    ret.setdefault("Tromino", {k for k, v in item_data_table.items() if "tromino" in v.tags})
    ret.setdefault("Tetromino", {k for k, v in item_data_table.items() if "tetromino" in v.tags})
    ret.setdefault("Pentomino", {k for k, v in item_data_table.items() if "pentomino" in v.tags})
    ret.setdefault("Shape", {k for k, v in item_data_table.items() if "shape" in v.tags})
    ret.setdefault("Rotate", {k for k, v in item_data_table.items() if "rotate" in v.tags})
    ret["Triomino"] = ret["Tromino"]
    ret["Piece"] = ret["Shape"]
    ret["Dracomino"] = ret["Shape"]
    ret["Mino"] = ret["Shape"]
    ret["Polyomino"] = ret["Shape"]
    ret.setdefault("Ability", {k for k, v in item_data_table.items() if "ability" in v.tags})
    return ret
    

item_data_table: Dict[str, DracominoItemData] = generate_item_map()
item_name_to_id = {name: data.code for name, data in item_data_table.items() if data.code is not None}
item_name_groups:Dict[str, Set[str]] = generate_item_name_groups()
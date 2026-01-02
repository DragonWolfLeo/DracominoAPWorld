from typing import Dict
from .Options import DracominoOptions

def get_shape_weights(options: DracominoOptions) -> Dict[str, int]:
    return {
        "monomino":  options.monomino_weight.value,
        "domino":    options.domino_weight.value,
        "tromino":   options.tromino_weight.value,
        "tetromino": options.tetromino_weight.value,
        "pentomino": options.pentomino_weight.value,
    }
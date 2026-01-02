VERSION:str = "0.2.0"
MIN_GAME_VERSION:str = "0.2.0"

BOARD_WIDTH:int = 10
BOARD_HEIGHT:int = 20
SHAPE_VALUES = {
    "monomino": 1,
    "domino": 2,
    "tromino": 3,
    "tetromino": 4,
    "pentomino": 5,
}

ITEMS = [
    # Abilities (1-100)
    [1,   "Gravity",                  [ "useful", "ability" ] ],
    [2,   "Soft Drop",                [ "useful", "ability" ] ],
    [3,   "Hard Drop",                [ "useful", "ability" ] ],
    [4,   "Rotate Clockwise",         [ "progression", "ability", "rotate" ] ],
    [5,   "Rotate Counterclockwise",  [ "progression", "ability", "rotate" ] ],
    [6,   "Ghost Piece",              [ "useful", "ability" ] ],

    # Progressive Items (101-200)
    [101, "Next Piece Slot",          [ "useful", "ability", "progressive" ] ],
    [102, "Hold Slot",                [ "useful", "ability", "progressive" ] ],
    
    # Traps Items (201-300)
    [201, "UNIMPLEMENTED TRAP",       [ "trap" ] ],
    
    # Shapes (301-)                                                                     Last two values are poor height, safe height
    [301, "Monomino",       [ "progression_skip_balancing", "shape", "monomino" ],                                             1, 1],

    [302, "Domino",         [ "progression_skip_balancing", "shape", "domino" ],                                               1, 2],

    [303, "I Tromino",      [ "progression_skip_balancing", "shape", "tromino" ],                                              1, 3],
    [304, "L Tromino",      [ "progression_skip_balancing", "shape", "tromino", "has_corner_gap" ],                            1, 2],

    [305, "I Tetromino",    [ "progression_skip_balancing", "shape", "tetromino" ],                                            1, 4],
    [306, "O Tetromino",    [ "progression_skip_balancing", "shape", "tetromino" ],                                            2, 2],
    [307, "T Tetromino",    [ "progression_skip_balancing", "shape", "tetromino", "has_corner_gap" ],                          1, 3],
    [308, "J Tetromino",    [ "progression_skip_balancing", "shape", "tetromino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [309, "L Tetromino",    [ "progression_skip_balancing", "shape", "tetromino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [310, "S Tetromino",    [ "progression_skip_balancing", "shape", "tetromino", "has_corner_gap" ],                          1, 2],
    [311, "Z Tetromino",    [ "progression_skip_balancing", "shape", "tetromino", "has_corner_gap" ],                          1, 2],

    [312, "I Pentomino",    [ "progression_skip_balancing", "shape", "pentomino" ],                                            1, 5],
    [313, "U Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_second_tile_gap" ],                     2, 3],
    [314, "T Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   2, 3],
    [315, "X Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap" ],                          2, 2],
    [316, "V Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [317, "W Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   2, 3],
    [318, "L Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 4],
    [319, "J Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 4],
    [320, "S Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [321, "Z Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [322, "F Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [323, "F' Pentomino",   [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [324, "N Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [325, "N' Pentomino",   [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [326, "P Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap" ],                          2, 3],
    [327, "Q Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap" ],                          2, 3],
    [328, "Y Pentomino",    [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
    [329, "Y' Pentomino",   [ "progression_skip_balancing", "shape", "pentomino", "has_corner_gap", "has_second_tile_gap" ],   1, 3],
]

LOCATIONS = [
    # Line Clears (1-1000)
    *([i,        f"Line {i} Cleared", [ "line_clear" ]] for i in range(1, 1001)),
    
    # Shape Clears (10001-20000)
    *([i + 10000, f"Coin {i}", [ "item_pickup" ]] for i in range(1, 10001)),
]
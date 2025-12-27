MATCH_HISTORY_FILE = "match_history.csv"

MIN_PLAYERS = 5
MAX_PLAYERS = 20
MAX_RESIDENTS = 15
MAX_TRAVELERS = 5

ROLE_COLORS = {
    "Townsfolk": "#00008B",
    "Outsider": "#ADD8E6",
    "Minion": "#FFA07A",
    "Demon": "#8B0000",
    "Traveler": "#A9A9A9",
}

STATUS_OPTIONS = {
    "Dead": {"bg": "#000000", "fg": "white"},
    "Poisoned": {"bg": "#800080", "fg": "white"},
    "Drunk": {"bg": "#006400", "fg": "white"},
    "Mad": {"bg": "#FF69B4", "fg": "black"},
    "Protected": {"bg": "#FFD700", "fg": "black"},
}

ROLE_DISTRIBUTION = {
    5:  (3, 0, 1, 1),
    6:  (3, 1, 1, 1),
    7:  (5, 0, 1, 1),
    8:  (5, 1, 1, 1),
    9:  (5, 2, 1, 1),
    10: (7, 0, 2, 1),
    11: (7, 1, 2, 1),
    12: (7, 2, 2, 1),
    13: (9, 0, 3, 1),
    14: (9, 1, 3, 1),
    15: (9, 2, 3, 1),
}

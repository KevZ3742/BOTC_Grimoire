def is_team_winner(player_class: str, winning_team: str) -> bool:
    """
    Check if a player's class is on the winning team
    
    Args:
        player_class: The class of the player (Townsfolk, Outsider, Minion, Demon)
        winning_team: The winning team (Townsfolk or Demon)
    
    Returns:
        True if the player's class is on the winning team
    """
    if winning_team == "Townsfolk":
        return player_class in ["Townsfolk", "Outsider"]
    elif winning_team == "Demon":
        return player_class in ["Demon", "Minion"]
    return False
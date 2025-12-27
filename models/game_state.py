from typing import List, Optional
from models.player import Player

class GameState:
    """Manages the current game state"""
    
    def __init__(self):
        self.players: List[Player] = []
        self.script_name: str = ""
        self.storyteller: str = ""
        self.bluff_roles: List[str] = []
        self.roles_generated: bool = False
    
    def add_player(self, player: Player):
        """Add a player to the game"""
        self.players.append(player)
    
    def clear(self):
        """Reset the game state"""
        self.players.clear()
        self.script_name = ""
        self.storyteller = ""
        self.bluff_roles.clear()
        self.roles_generated = False
    
    def get_residents(self) -> List[Player]:
        """Get all resident players"""
        return [p for p in self.players if not p.is_traveler]
    
    def get_travelers(self) -> List[Player]:
        """Get all traveler players"""
        return [p for p in self.players if p.is_traveler]
    
    def validate_usernames(self) -> tuple[bool, str]:
        """Validate that all usernames are present and unique"""
        usernames = [p.username for p in self.players]
        
        if any(not u.strip() for u in usernames):
            return False, "All usernames are required"
        
        if len(usernames) != len(set(usernames)):
            return False, "Usernames must be unique"
        
        return True, ""
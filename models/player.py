from dataclasses import dataclass, field
from typing import Set, Optional

@dataclass
class Player:
    """Represents a player in the game"""
    username: str
    role: str
    player_class: str  # Townsfolk, Outsider, Minion, Demon, Traveler
    is_traveler: bool = False
    status_tags: Set[str] = field(default_factory=set)
    drunk_fake_role: Optional[str] = None
    
    def add_status(self, status: str):
        """Add a status tag to the player"""
        self.status_tags.add(status)
    
    def remove_status(self, status: str):
        """Remove a status tag from the player"""
        self.status_tags.discard(status)
    
    def clear_statuses(self):
        """Clear all status tags"""
        self.status_tags.clear()
    
    def get_actual_role(self) -> str:
        """Get the actual role (handling Drunk)"""
        if self.role.startswith("Drunk-"):
            return "Drunk"
        return self.role
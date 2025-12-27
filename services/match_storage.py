import csv
import os
import time
from typing import List, Dict
from config.constants import MATCH_HISTORY_FILE
from models.player import Player

class MatchStorage:
    """Handles saving and loading match history"""
    
    @staticmethod
    def save_match(players: List[Player], winning_team: str, 
                   storyteller: str, script: str):
        """Save a match to the CSV file"""
        game_id = str(int(time.time()))
        match_id = f"{game_id}|{winning_team}|{storyteller}|{script}"
        
        with open(MATCH_HISTORY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            for player in players:
                role = player.get_actual_role()
                player_won = MatchStorage._is_player_winner(
                    player.player_class, winning_team
                )
                
                writer.writerow([
                    match_id,
                    player.player_class,
                    player.username,
                    role,
                    "Win" if player_won else "Loss"
                ])
    
    @staticmethod
    def load_matches() -> List[Dict]:
        """Load all matches from the CSV file"""
        if not os.path.exists(MATCH_HISTORY_FILE):
            return []
        
        matches = []
        with open(MATCH_HISTORY_FILE, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 4:
                    continue
                
                match_id = row[0]
                parts = match_id.split("|")
                
                if len(parts) != 4:
                    continue
                
                game_id, winner, storyteller, script = parts
                
                # Handle old format without result field
                if len(row) >= 5:
                    result = row[4]
                else:
                    result = "Win" if MatchStorage._is_player_winner(row[1], winner) else "Loss"
                
                matches.append({
                    "game_id": game_id,
                    "winner": winner,
                    "storyteller": storyteller,
                    "script": script,
                    "class": row[1],
                    "username": row[2],
                    "role": row[3],
                    "result": result
                })
        
        return matches
    
    @staticmethod
    def _is_player_winner(player_class: str, winning_team: str) -> bool:
        """Check if a player's class is on the winning team"""
        if winning_team == "Townsfolk":
            return player_class in ["Townsfolk", "Outsider"]
        elif winning_team == "Demon":
            return player_class in ["Demon", "Minion"]
        return False
    
    @staticmethod
    def get_all_usernames() -> set:
        """Get all unique usernames from match history"""
        matches = MatchStorage.load_matches()
        return {m["username"] for m in matches}
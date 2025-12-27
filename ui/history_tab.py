import tkinter as tk
from tkinter import ttk
from services.match_storage import MatchStorage

class HistoryTab:
    """Match history tab"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI"""
        history_frame = ttk.Frame(self.frame)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create treeview
        self.tree = ttk.Treeview(history_frame)
        self.tree.pack(fill='both', expand=True)
        
        # Configure columns
        self.tree["columns"] = ("class", "username", "role")
        self.tree.heading("#0", text="Match")
        self.tree.heading("class", text="Class")
        self.tree.heading("username", text="Username")
        self.tree.heading("role", text="Role")
        self.tree.column("class", width=100)
        self.tree.column("username", width=150)
        self.tree.column("role", width=150)
        
        # Configure tag colors
        townsfolk_win_color = "#00008B"  # Dark blue for town wins
        demon_win_color = "#8B0000"      # Dark red for demon wins
        win_color = "#90EE90"            # Light green for wins
        loss_color = "#FFCCCB"           # Light red for losses
        
        # Parent rows - dark team colors with white text
        self.tree.tag_configure("townsfolk_win", 
                               background=townsfolk_win_color, 
                               foreground="white")
        self.tree.tag_configure("demon_win", 
                               background=demon_win_color, 
                               foreground="white")
        
        # Child rows - light win/loss colors with black text
        self.tree.tag_configure("win", 
                               background=win_color, 
                               foreground="black")
        self.tree.tag_configure("loss", 
                               background=loss_color, 
                               foreground="black")
    
    def load_history(self):
        """Load match history into the tree"""
        # Clear existing
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Load matches
        matches = MatchStorage.load_matches()
        
        # Group by match_id
        grouped = {}
        for match in reversed(matches):  # Newest first
            match_id = f"{match['game_id']}|{match['winner']}|{match['storyteller']}|{match['script']}"
            if match_id not in grouped:
                grouped[match_id] = []
            grouped[match_id].append(match)
        
        # Populate tree
        for match_id, entries in grouped.items():
            parts = match_id.split("|")
            game_id, winner, storyteller, script = parts
            
            # Parent row
            parent_tag = "townsfolk_win" if winner == "Townsfolk" else "demon_win"
            parent = self.tree.insert(
                "", "end",
                text=f"Game {game_id} | Winner: {winner} | Storyteller: {storyteller} | Script: {script}",
                open=False,
                tags=(parent_tag,)
            )
            
            # Child rows
            for entry in entries:
                tag = entry["result"].lower()
                self.tree.insert(
                    parent, "end",
                    values=(entry["class"], entry["username"], entry["role"]),
                    tags=(tag,)
                )
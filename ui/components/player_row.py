import tkinter as tk
from tkinter import ttk
from typing import List
from config.constants import ROLE_COLORS
from models.player import Player
from ui.components.status_tags import StatusTagWidget

class PlayerRowManager:
    """Manages the player row table"""
    
    def __init__(self, parent, num_residents: int, num_travelers: int):
        self.parent = parent
        self.num_residents = num_residents
        self.num_travelers = num_travelers
        self.rows = []
        
        self._create_table()
    
    def _create_table(self):
        """Create the player table with headers"""
        # Clear existing
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.rows.clear()
        
        # Headers
        headers = ["Class", "Username", "Role", "Status Tags"]
        for col, text in enumerate(headers):
            header = ttk.Label(self.parent, text=text, 
                             font=('Arial', 10, 'bold'),
                             borderwidth=1, relief="solid")
            header.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        
        # Configure columns
        for col in range(len(headers)):
            self.parent.columnconfigure(col, weight=1)
        
        # Create rows
        for i in range(self.num_residents + self.num_travelers):
            self._create_row(i)
    
    def _create_row(self, index: int):
        """Create a single player row"""
        is_traveler = index >= self.num_residents
        row_num = index + 1
        
        # Class label
        class_lbl = tk.Label(self.parent,
                           text="Traveler" if is_traveler else "Resident",
                           width=10, borderwidth=1, relief="solid")
        class_lbl.grid(row=row_num, column=0, padx=5, pady=2, sticky="nsew")
        
        # Username entry
        username_entry = ttk.Entry(self.parent)
        username_entry.grid(row=row_num, column=1, padx=5, pady=2, sticky="nsew")
        
        # Role label
        role_lbl = ttk.Label(self.parent, text="TBD",
                           borderwidth=1, relief="solid")
        role_lbl.grid(row=row_num, column=2, padx=5, pady=2, sticky="nsew")
        
        # Status tag widget
        status_widget = StatusTagWidget(self.parent)
        status_widget.grid(row=row_num, column=3, padx=5, pady=2, sticky="nsew")
        
        self.rows.append({
            "class_label": class_lbl,
            "username_entry": username_entry,
            "role_label": role_lbl,
            "status_widget": status_widget,
            "is_traveler": is_traveler
        })
    
    def update_roles(self, players: List[Player]):
        """Update the roles in the UI from player list"""
        for i, (row, player) in enumerate(zip(self.rows, players)):
            # Update role
            row["role_label"].config(text=player.role)
            
            # Update class
            row["class_label"].config(text=player.player_class)
            self._color_class_label(row["class_label"], player.player_class)
    
    def _color_class_label(self, label, role_type: str):
        """Apply color to class label"""
        color = ROLE_COLORS.get(role_type, "#FFFFFF")
        fg_color = "white" if role_type in ["Townsfolk", "Demon"] else "black"
        label.config(background=color, foreground=fg_color)
    
    def fill_player_usernames(self, players: List[Player]) -> bool:
        """Fill player usernames from UI entries. Returns True if all valid."""
        for row, player in zip(self.rows, players):
            username = row["username_entry"].get().strip()
            if not username:
                return False
            player.username = username
            
            # Also get status tags
            player.status_tags = row["status_widget"].get_active_tags()
        
        return True
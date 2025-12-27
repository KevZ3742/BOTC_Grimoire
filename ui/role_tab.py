import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from scripts import scripts
from config.constants import MIN_PLAYERS, MAX_RESIDENTS, MAX_TRAVELERS, MAX_PLAYERS
from models.game_state import GameState
from services.role_generator import RoleGenerator
from services.match_storage import MatchStorage
from ui.components.player_row import PlayerRowManager

class RoleTab:
    """Role generator tab"""
    
    def __init__(self, parent, game_state: GameState, on_match_saved: Callable):
        self.frame = ttk.Frame(parent)
        self.game_state = game_state
        self.on_match_saved = on_match_saved
        self.player_row_manager = None
        
        self._build_ui()
    
    def _build_ui(self):
        # Script selector
        ttk.Label(self.frame, text="Select Script:").pack(pady=5)
        self.script_var = tk.StringVar()
        script_dropdown = ttk.Combobox(self.frame, textvariable=self.script_var, 
                                      state="readonly")
        script_dropdown['values'] = list(scripts.keys())
        script_dropdown.current(0)
        script_dropdown.pack(pady=5)
        
        # Storyteller input
        storyteller_frame = ttk.Frame(self.frame)
        storyteller_frame.pack(pady=5)
        ttk.Label(storyteller_frame, text="Storyteller:").pack(side=tk.LEFT, padx=5)
        self.storyteller_var = tk.StringVar()
        ttk.Entry(storyteller_frame, textvariable=self.storyteller_var, 
                 width=20).pack(side=tk.LEFT)
        
        # Player count input
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(pady=5)
        ttk.Label(input_frame, text="Number of Players (5–15):").pack(
            side=tk.LEFT, padx=5)
        self.player_count_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.player_count_var, 
                 width=5).pack(side=tk.LEFT)
        ttk.Label(input_frame, text="Number of Travelers (0–5):").pack(
            side=tk.LEFT, padx=5)
        self.traveler_count_var = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.traveler_count_var, 
                 width=5).pack(side=tk.LEFT)
        ttk.Button(input_frame, text="Create Rows", 
                  command=self.create_rows).pack(side=tk.LEFT, padx=10)
        
        # Main content area
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(pady=10)
        
        # Player table
        self.player_table_frame = ttk.Frame(main_frame)
        self.player_table_frame.grid(row=0, column=0, padx=10)
        
        # Info frame (placeholder)
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=1, padx=10)
        self.create_prompt_label = ttk.Label(info_frame, 
                                            text="Create rows first", 
                                            foreground="gray", anchor="center")
        self.create_prompt_label.pack(fill='x', pady=20)
        
        # Bluff roles
        bluff_frame = ttk.LabelFrame(main_frame, text="Bluff Roles for Demon")
        bluff_frame.grid(row=0, column=2, padx=10)
        self.bluff_labels = [ttk.Label(bluff_frame, text=f"Bluff {i+1}: TBD", 
                                       anchor="center") for i in range(3)]
        for lbl in self.bluff_labels:
            lbl.pack(padx=5, pady=2, fill=tk.X)
        
        # Generate button
        ttk.Button(self.frame, text="Generate Roles", 
                  command=self.generate_roles).pack(pady=5)
        
        # Win buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        
        btn_townsfolk = tk.Button(button_frame, text="Townsfolk Win", 
                                 bg="#00008B", fg="white",
                                 command=lambda: self.save_and_reset("Townsfolk"))
        btn_townsfolk.grid(row=0, column=0, padx=10)
        
        btn_demon = tk.Button(button_frame, text="Demons Win", 
                             bg="#8B0000", fg="white",
                             command=lambda: self.save_and_reset("Demon"))
        btn_demon.grid(row=0, column=1, padx=10)
    
    def create_rows(self):
        """Create player rows based on input"""
        try:
            num_players = int(self.player_count_var.get())
            num_travelers = int(self.traveler_count_var.get())
            
            if not (MIN_PLAYERS <= num_players <= MAX_RESIDENTS):
                raise ValueError
            if not (0 <= num_travelers <= MAX_TRAVELERS):
                raise ValueError
            if num_players + num_travelers > MAX_PLAYERS:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Players: 5-15, Travelers: 0-5, Total ≤ 20")
            return
        
        # Hide prompt
        self.create_prompt_label.pack_forget()
        
        # Create player row manager
        self.player_row_manager = PlayerRowManager(
            self.player_table_frame, num_players, num_travelers
        )
    
    def generate_roles(self):
        """Generate roles for all players"""
        if not self.player_row_manager:
            messagebox.showerror("No Rows", "Click 'Create Rows' first.")
            return
        
        script_name = self.script_var.get()
        script_roles = scripts.get(script_name)
        
        num_residents = self.player_row_manager.num_residents
        num_travelers = self.player_row_manager.num_travelers
        
        try:
            players, bluff_roles = RoleGenerator.generate_roles(
                num_residents, num_travelers, script_roles
            )
        except ValueError as e:
            messagebox.showerror("Generation Error", str(e))
            return
        
        # Update UI
        self.player_row_manager.update_roles(players)
        
        # Update bluffs
        for i, bluff in enumerate(bluff_roles):
            self.bluff_labels[i].config(text=f"Bluff {i+1}: {bluff}")
        
        # Update game state
        self.game_state.players = players
        self.game_state.script_name = script_name
        self.game_state.bluff_roles = bluff_roles
        self.game_state.roles_generated = True
    
    def save_and_reset(self, winning_team: str):
        """Save match and reset"""
        if not self.game_state.roles_generated:
            messagebox.showerror("Roles Not Generated", 
                               "You must generate roles before ending the game.")
            return
        
        # Confirm
        team_members = ("Townsfolk and Outsiders" if winning_team == "Townsfolk" 
                       else "Demons and Minions")
        if not messagebox.askyesno("Confirm End Game",
                                   f"Are you sure you want to end the game with "
                                   f"{team_members} winning?"):
            return
        
        # Validate storyteller
        storyteller = self.storyteller_var.get().strip()
        if not storyteller:
            messagebox.showerror("Missing Storyteller", 
                               "Storyteller name is required before saving.")
            return
        
        # Get usernames from UI
        if not self.player_row_manager.fill_player_usernames(self.game_state.players):
            messagebox.showerror("Missing Usernames", 
                               "All usernames are required before saving.")
            return
        
        # Validate
        valid, error = self.game_state.validate_usernames()
        if not valid:
            messagebox.showerror("Invalid Data", error)
            return
        
        # Save
        try:
            MatchStorage.save_match(
                self.game_state.players,
                winning_team,
                storyteller,
                self.game_state.script_name
            )
            self.on_match_saved()
            self.reset()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save match: {e}")
    
    def reset(self):
        """Reset the tab"""
        self.script_var.set(list(scripts.keys())[0])
        self.storyteller_var.set("")
        self.player_count_var.set("")
        self.traveler_count_var.set("0")
        
        # Clear player table
        for widget in self.player_table_frame.winfo_children():
            widget.destroy()
        self.player_row_manager = None
        
        # Reset bluffs
        for i, lbl in enumerate(self.bluff_labels):
            lbl.config(text=f"Bluff {i+1}: TBD")
        
        # Show prompt again
        self.create_prompt_label.pack(fill='x', pady=20)
        
        # Clear game state
        self.game_state.clear()
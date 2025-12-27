import tkinter as tk
from tkinter import ttk
from ui.role_tab import RoleTab
from ui.history_tab import HistoryTab
from ui.search_tab import SearchTab
from models.game_state import GameState

class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Blood on the Clocktower Grimoire")
        self.root.geometry("1100x650")
        
        # Shared game state
        self.game_state = GameState()
        
        # Create notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.role_tab = RoleTab(self.notebook, self.game_state, self.on_match_saved)
        self.history_tab = HistoryTab(self.notebook)
        self.search_tab = SearchTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.role_tab.frame, text='Role Generator')
        self.notebook.add(self.history_tab.frame, text='Match History')
        self.notebook.add(self.search_tab.frame, text='Player Search')
        
        # Initial load
        self.history_tab.load_history()
        self.search_tab.load_data()
    
    def on_match_saved(self):
        """Callback when a match is saved"""
        self.history_tab.load_history()
        self.search_tab.load_data()
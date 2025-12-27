import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from scripts import scripts
from services.match_storage import MatchStorage

class SearchTab:
    """Player search tab"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.all_usernames = set()
        self.match_data: List[Dict] = []
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI"""
        # Search input
        search_label = ttk.Label(self.frame, text="Search Player:")
        search_label.pack(pady=(20, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var)
        self.search_entry.pack(pady=5, padx=20, fill='x')
        
        # Autocomplete listbox
        self.autocomplete_listbox = tk.Listbox(self.frame, height=6)
        self.autocomplete_listbox.pack(padx=20, fill='x')
        self.autocomplete_listbox.place_forget()  # Hide initially
        
        # Player stats frame
        player_stats_frame = ttk.LabelFrame(self.frame, text="Player Stats")
        player_stats_frame.pack(padx=20, pady=10, fill='x')
        
        self.winrate_label = ttk.Label(player_stats_frame, 
                                       text="Overall Win Rate: N/A")
        self.winrate_label.pack(pady=5)
        
        # Script filter
        self.script_filter_var = tk.StringVar()
        self.script_filter_dropdown = ttk.Combobox(
            player_stats_frame, 
            textvariable=self.script_filter_var, 
            state="readonly"
        )
        self.script_filter_dropdown['values'] = ['All'] + list(scripts.keys())
        self.script_filter_dropdown.current(0)
        self.script_filter_dropdown.pack(pady=5)
        
        self.script_winrate_label = ttk.Label(
            player_stats_frame, 
            text="Win Rate for Selected Script: N/A"
        )
        self.script_winrate_label.pack(pady=5)
        
        # Per-role win rate frame
        role_stats_frame = ttk.LabelFrame(player_stats_frame, 
                                         text="Role Win Rates for Selected Script")
        role_stats_frame.pack(pady=10, fill="both", expand=True)
        
        self.role_stats_text = tk.Text(role_stats_frame, height=10, width=50, 
                                       state="disabled")
        self.role_stats_text.pack(padx=5, pady=5)
        
        # Bindings
        self.search_entry.bind("<KeyRelease>", self._update_autocomplete)
        self.autocomplete_listbox.bind("<<ListboxSelect>>", self._on_select)
        self.script_filter_dropdown.bind("<<ComboboxSelected>>", 
                                        self._on_script_change)
    
    def load_data(self):
        """Load all match data"""
        self.match_data = MatchStorage.load_matches()
        self.all_usernames = {m["username"] for m in self.match_data}
    
    def _update_autocomplete(self, event=None):
        """Update autocomplete suggestions"""
        typed = self.search_var.get().lower()
        matches = [u for u in self.all_usernames if typed in u.lower()]
        
        if matches and typed:
            self.autocomplete_listbox.delete(0, tk.END)
            for u in matches[:10]:
                self.autocomplete_listbox.insert(tk.END, u)
            self.autocomplete_listbox.place(
                x=self.search_entry.winfo_x(), 
                y=self.search_entry.winfo_y() + self.search_entry.winfo_height()
            )
            self.autocomplete_listbox.lift()
        else:
            self.autocomplete_listbox.place_forget()
    
    def _on_select(self, event):
        """Handle autocomplete selection"""
        if not self.autocomplete_listbox.curselection():
            return
        
        selected = self.autocomplete_listbox.get(
            self.autocomplete_listbox.curselection()
        )
        self.search_var.set(selected)
        self.autocomplete_listbox.place_forget()
        
        # Reset script filter
        self.script_filter_var.set('All')
        
        # Display stats
        self._display_player_stats(selected)
    
    def _on_script_change(self, event=None):
        """Handle script filter change"""
        username = self.search_var.get()
        if username:
            self._update_script_stats(username)
    
    def _display_player_stats(self, username: str):
        """Display stats for a player"""
        user_matches = [m for m in self.match_data if m["username"] == username]
        
        if not user_matches:
            self.winrate_label.config(
                text=f"Overall Win Rate for {username}: N/A"
            )
            self.script_winrate_label.config(
                text="Win Rate for Selected Script: N/A"
            )
            self._update_role_stats_text("No data for this player.")
            return
        
        # Overall win rate
        wins = sum(1 for m in user_matches if m["result"] == "Win")
        total = len(user_matches)
        rate = wins / total * 100
        self.winrate_label.config(
            text=f"Overall Win Rate for {username}: {rate:.2f}% ({wins}/{total})"
        )
        
        # Update script-specific stats
        self._update_script_stats(username)
    
    def _update_script_stats(self, username: str):
        """Update stats for selected script"""
        selected_script = self.script_filter_var.get()
        user_matches = [m for m in self.match_data if m["username"] == username]
        
        # Filter by script if not "All"
        if selected_script != "All":
            user_matches = [m for m in user_matches 
                          if m["script"] == selected_script]
        
        if not user_matches:
            self.script_winrate_label.config(
                text="Win Rate for Selected Script: N/A"
            )
            self._update_role_stats_text("No matches for this script.")
            return
        
        # Script win rate
        wins = sum(1 for m in user_matches if m["result"] == "Win")
        total = len(user_matches)
        rate = wins / total * 100
        self.script_winrate_label.config(
            text=f"Win Rate for Selected Script: {rate:.2f}% ({wins}/{total})"
        )
        
        # Per-role stats
        role_stats = {}
        for m in user_matches:
            role = m["role"]
            if role not in role_stats:
                role_stats[role] = {"wins": 0, "total": 0}
            role_stats[role]["total"] += 1
            if m["result"] == "Win":
                role_stats[role]["wins"] += 1
        
        # Format role stats
        lines = []
        for role, stats in sorted(role_stats.items()):
            role_winrate = (stats["wins"] / stats["total"]) * 100
            lines.append(
                f"{role}: {role_winrate:.2f}% ({stats['wins']}/{stats['total']})"
            )
        
        self._update_role_stats_text("\n".join(lines))
    
    def _update_role_stats_text(self, text: str):
        """Update the role stats text widget"""
        self.role_stats_text.config(state="normal")
        self.role_stats_text.delete(1.0, tk.END)
        self.role_stats_text.insert(tk.END, text)
        self.role_stats_text.config(state="disabled")
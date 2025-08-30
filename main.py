import tkinter as tk
from tkinter import ttk, messagebox
import random
import csv
import os
import time
from scripts import scripts
import types

# Constants
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

roles_generated = False

role_distribution = {
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

STATUS_OPTIONS = {
    # Format: {"status": {"bg": color, "fg": color}}
    "Dead": {"bg": "#000000", "fg": "white"},
    "Poisoned": {"bg": "#800080", "fg": "white"},
    "Drunk": {"bg": "#006400", "fg": "white"},
    "Mad": {"bg": "#FF69B4", "fg": "black"},
    "Protected": {"bg": "#FFD700", "fg": "black"},
}

root = tk.Tk()
root.title("Blood on the Clocktower Grimoire")
root.geometry("1100x650")
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# --- Tabs ---
role_tab = ttk.Frame(notebook)
match_tab = ttk.Frame(notebook)
search_tab = ttk.Frame(notebook)  # New Player Search tab
notebook.add(role_tab, text='Role Generator')
notebook.add(match_tab, text='Match History')
notebook.add(search_tab, text='Player Search')

# --- Role Generator UI ---
ttk.Label(role_tab, text="Select Script:").pack(pady=5)
script_var = tk.StringVar()
script_dropdown = ttk.Combobox(role_tab, textvariable=script_var, state="readonly")
script_dropdown['values'] = list(scripts.keys())
script_dropdown.current(0)
script_dropdown.pack(pady=5)

storyteller_frame = ttk.Frame(role_tab)
storyteller_frame.pack(pady=5)
ttk.Label(storyteller_frame, text="Storyteller:").pack(side=tk.LEFT, padx=5)
storyteller_username_var = tk.StringVar()
ttk.Entry(storyteller_frame, textvariable=storyteller_username_var, width=20).pack(side=tk.LEFT)

input_frame = ttk.Frame(role_tab)
input_frame.pack(pady=5)
ttk.Label(input_frame, text="Number of Players (5–15):").pack(side=tk.LEFT, padx=5)
player_count_var = tk.StringVar()
ttk.Entry(input_frame, textvariable=player_count_var, width=5).pack(side=tk.LEFT)
ttk.Label(input_frame, text="Number of Travelers (0–5):").pack(side=tk.LEFT, padx=5)
traveler_count_var = tk.StringVar(value="0")
ttk.Entry(input_frame, textvariable=traveler_count_var, width=5).pack(side=tk.LEFT)
create_btn = ttk.Button(input_frame, text="Create Rows")
create_btn.pack(side=tk.LEFT, padx=10)

main_frame = ttk.Frame(role_tab)
main_frame.pack(pady=10)
player_table_frame = ttk.Frame(main_frame)
player_table_frame.grid(row=0, column=0, padx=10)

info_frame = ttk.Frame(main_frame)
info_frame.grid(row=0, column=1, padx=10)
create_prompt_label = ttk.Label(info_frame, text="Create rows first", foreground="gray", anchor="center")
create_prompt_label.pack(fill='x', pady=20)

bluff_frame = ttk.LabelFrame(main_frame, text="Bluff Roles for Demon")
bluff_frame.grid(row=0, column=2, padx=10)
bluff_labels = [ttk.Label(bluff_frame, text=f"Bluff {i+1}: TBD", anchor="center") for i in range(3)]
for lbl in bluff_labels:
    lbl.pack(padx=5, pady=2, fill=tk.X)

player_rows = []

# --- Create Rows ---
def color_class_label(label, role_type):
    color = ROLE_COLORS.get(role_type, "#FFFFFF")
    fg_color = "white" if role_type in ["Townsfolk", "Demon"] else "black"
    label.config(background=color, foreground=fg_color)

def create_player_rows():
    # Clear existing rows
    for widget in player_table_frame.winfo_children():
        widget.destroy()
    player_rows.clear()
    
    # Validate input
    try:
        num_players = int(player_count_var.get())
        num_travelers = int(traveler_count_var.get())
        if not (5 <= num_players <= MAX_RESIDENTS) or not (0 <= num_travelers <= MAX_TRAVELERS):
            raise ValueError
        if num_players + num_travelers > MAX_PLAYERS:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Players: 5-15, Travelers: 0-5, Total ≤ 20")
        return
    
    create_prompt_label.pack_forget()
    
    # Create column headers
    headers = ["Class", "Username", "Role", "Status Tags"]
    for col, text in enumerate(headers):
        header = ttk.Label(player_table_frame, 
                         text=text, 
                         font=('Arial', 10, 'bold'),
                         borderwidth=1,
                         relief="solid")
        header.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
    
    # Configure column weights
    for col in range(len(headers)):
        player_table_frame.columnconfigure(col, weight=1)
    
    # Create player rows
    for i in range(num_players + num_travelers):
        is_traveler = i >= num_players
        
        # Class Label
        class_lbl = tk.Label(player_table_frame,
                           text="Traveler" if is_traveler else "Resident",
                           width=10,
                           borderwidth=1,
                           relief="solid")
        class_lbl.grid(row=i+1, column=0, padx=5, pady=2, sticky="nsew")
        
        # Username Entry
        username_entry = ttk.Entry(player_table_frame)
        username_entry.grid(row=i+1, column=1, padx=5, pady=2, sticky="nsew")
        
        # Role Label
        role_lbl = ttk.Label(player_table_frame,
                           text="TBD",
                           borderwidth=1,
                           relief="solid")
        role_lbl.grid(row=i+1, column=2, padx=5, pady=2, sticky="nsew")
        
        # Status Tag Cell
        tag_frame = tk.Frame(player_table_frame,
               borderwidth=1,
               relief="solid")
        tag_frame.grid(row=i+1, column=3, padx=5, pady=2, sticky="nsew")
        tag_frame.grid_propagate(True)

        # Frame to hold colored squares
        tag_squares_frame = tk.Frame(tag_frame)
        tag_squares_frame.pack(expand=True, fill="both")

        tag_label = tk.Label(tag_frame, text="", anchor="w", padx=0, pady=0)
        tag_label.active_tags = set()

        # Create a context object to hold our references
        class StatusContext:
            def __init__(self, label, frame, menu):
                self.label = label
                self.frame = frame
                self.menu = menu
                self.menu_indices = []
                
            def make_toggle_command(self, status):
                def cmd():
                    toggle_status_tag(self.label, status)
                    self.update_tag_display()
                    self.update_menu_checks()
                return cmd
                
            def clear_command(self):
                def cmd():
                    clear_status_tags(self.label)
                    self.update_tag_display()
                    self.update_menu_checks()
                return cmd
                
            def update_menu_checks(self):
                for idx, status, color in self.menu_indices:
                    checked = status in self.label.active_tags
                    check = "✓ " if checked else ""
                    self.menu.entryconfig(idx, label=f"{check}\u25A0 {status}", foreground=color)
                    
            def update_tag_display(self):
                for widget in self.frame.winfo_children():
                    widget.destroy()
                
                for status in self.label.active_tags:
                    colors = STATUS_OPTIONS.get(status, {"bg": "#CCCCCC", "fg": "black"})
                    square = tk.Label(
                        self.frame,
                        bg=colors["bg"],
                        fg=colors["fg"],
                        text=status,
                        width=max(7, len(status)),
                        height=1,
                        relief="ridge",
                        borderwidth=1,
                        font=("Arial", 9, "bold")
                    )
                    square.pack(side="left", padx=2, pady=1)
                    square.bind("<Button-3>", self.show_menu)
                self.label.config(text="")
                
            def show_menu(self, event=None):
                self.update_menu_checks()
                self.menu.post(event.x_root, event.y_root)

        # Create the context with our current widgets
        context = StatusContext(tag_label, tag_squares_frame, tk.Menu(root, tearoff=0))

        # Add status options to the menu
        for idx, (status, colors) in enumerate(STATUS_OPTIONS.items()):
            context.menu.add_command(
                label=f"\u25A0 {status}",
                command=context.make_toggle_command(status)
            )
            context.menu.entryconfig(idx, foreground=colors["bg"])
            context.menu_indices.append((idx, status, colors["bg"]))

        context.menu.add_separator()
        context.menu.add_command(
            label="Clear all statuses",
            command=context.clear_command()
        )

        # Bind right-click to show menu
        tag_frame.bind("<Button-3>", context.show_menu)
        tag_squares_frame.bind("<Button-3>", context.show_menu)

        # Visual feedback on hover
        tag_frame.bind("<Enter>", lambda _: tag_frame.config(relief="groove"))
        tag_frame.bind("<Leave>", lambda _: tag_frame.config(relief="solid"))

        # Store the update method
        tag_label.update_tag_display = context.update_tag_display

        player_rows.append({
            "username_entry": username_entry,
            "role_label": role_lbl,
            "class_label": class_lbl,
            "tag_label": tag_label,
            "is_traveler": is_traveler,
            "tag_squares_frame": tag_squares_frame
        })
create_btn.config(command=create_player_rows)

def toggle_status_tag(label, status):
    if status in label.active_tags:
        label.active_tags.remove(status)
    else:
        label.active_tags.add(status)
    update_tag_display(label)

def clear_status_tags(label):
    label.active_tags.clear()
    update_tag_display(label)

def update_tag_display(label):
    if not label.active_tags:
        label.config(text="")
        return
    
    label.config(text=", ".join(label.active_tags))

# --- Generate Roles ---
def generate_roles():
    global roles_generated
    if not player_rows:
        messagebox.showerror("No Rows", "Click 'Create Rows' first.")
        return

    script_name = script_var.get()
    roles = scripts.get(script_name)

    num_players = sum(1 for r in player_rows if not r["is_traveler"])

    if num_players < MIN_PLAYERS:
        messagebox.showerror("Too Few", "Need at least 5 residents.")
        return

    try:
        townsfolk, outsiders, minions, demons = role_distribution[num_players]
    except KeyError:
        messagebox.showerror("Unsupported", "Only 5–15 residents supported.")
        return

    # We'll generate roles to check if Baron is in the pool later:

    init_minions = random.sample(roles["Minion"], minions)
    role_pool_full = (
        random.sample(roles["Townsfolk"], townsfolk) +
        random.sample(roles["Outsider"], outsiders) +
        random.sample(roles["Demon"], demons) + init_minions
    )

    # Adjust for Baron role if present in script or role_pool_full
    # We check if Baron is in the combined pool
    if "Baron" in role_pool_full:
        # Baron adjustment: +2 Outsiders, -2 Townsfolk
        townsfolk -= 2
        outsiders += 2
        if townsfolk < 0:
            townsfolk = 0  # Don't allow negative
    if "Godfather" in role_pool_full:
        # Baron adjustment: +2 Outsiders, -2 Townsfolk
        if random.randint(0, 1) == 0:
            townsfolk -= 1
            outsiders += 1
        else:
            townsfolk += 1
            outsiders -= 1
        if townsfolk < 0:
            townsfolk = 0  # Don't allow negative

    # Now sample final roles again with adjusted counts
    try:
        final_townsfolk = random.sample(roles["Townsfolk"], townsfolk)
        final_outsiders = random.sample(roles["Outsider"], outsiders)
        final_demons = random.sample(roles["Demon"], demons)
    except ValueError as e:
        messagebox.showerror("Role Sampling Error", f"Not enough roles to sample: {e}")
        return

    role_pool = final_townsfolk + final_outsiders + init_minions + final_demons
    random.shuffle(role_pool)

    traveler_roles = roles.get("Traveler", [])[:]
    random.shuffle(traveler_roles)

    for row in player_rows:
        if not row["is_traveler"]:
            role = role_pool.pop()
            row["role_label"].config(text=role)
            for rtype in ["Townsfolk", "Outsider", "Minion", "Demon"]:
                if role in roles[rtype]:
                    row["class_label"].config(text=rtype)
                    color_class_label(row["class_label"], rtype)
                    break
        else:
            role = traveler_roles.pop() if traveler_roles else "Traveler"
            row["role_label"].config(text=role)
            row["class_label"].config(text="Traveler")
            color_class_label(row["class_label"], "Traveler")

    all_townsfolk = [r for r in roles["Townsfolk"] if r != "Drunk"]
    assigned_roles = [row["role_label"].cget("text") for row in player_rows]

    # remove any roles that are already assigned to real players
    eligible_fake_roles = [r for r in all_townsfolk if r not in assigned_roles]

    for row in player_rows:
        if row["role_label"].cget("text") == "Drunk":
            fake_role = random.choice(eligible_fake_roles) if eligible_fake_roles else "unknown"
            row["role_label"].drunk_fake_role = fake_role
            row["role_label"].config(text=f"Drunk-{fake_role}")

    bluff_pool = [r for r in roles["Townsfolk"] + roles["Outsider"] if r not in assigned_roles]
    random.shuffle(bluff_pool)
    for i in range(3):
        bluff = bluff_pool.pop() if bluff_pool else "TBD"
        bluff_labels[i].config(text=f"Bluff {i+1}: {bluff}")

    roles_generated = True  # Set flag when roles are generated

ttk.Button(role_tab, text="Generate Roles", command=generate_roles).pack(pady=5)

# --- Save and Reset ---
def save_and_reset(winning_team):
    global roles_generated
    
    if not roles_generated:
        messagebox.showerror("Roles Not Generated", "You must generate roles before ending the game.")
        return
    
    team_members = "Townsfolk and Outsiders" if winning_team == "Townsfolk" else "Demons and Minions"
    confirm = messagebox.askyesno(
        "Confirm End Game",
        f"Are you sure you want to end the game with {team_members} winning?",
        icon='question'
    )
    if not confirm:
        return
    
    if not storyteller_username_var.get().strip():
        messagebox.showerror("Missing Storyteller", "Storyteller name is required before saving.")
        return

    usernames = []
    for row in player_rows:
        uname = row['username_entry'].get().strip()
        if not uname:
            messagebox.showerror("Missing Usernames", "All usernames are required before saving.")
            return
        usernames.append(uname)
    if len(usernames) != len(set(usernames)):
        messagebox.showerror("Duplicate Usernames", "Usernames must be unique.")
        return

    script = script_var.get()
    storyteller = storyteller_username_var.get().strip()
    game_id = str(int(time.time()))
    
    # Format: game_id|winning_team|storyteller|script
    match_id = f"{game_id}|{winning_team}|{storyteller}|{script}"

    with open(MATCH_HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for row in player_rows:
            role = row["role_label"].cget("text")
            if hasattr(row["role_label"], 'drunk_fake_role'):
                role = "Drunk"
            
            # Determine if this player's team won
            player_class = row["class_label"].cget("text")
            if player_class in ["Townsfolk", "Outsider"]:
                player_won = winning_team == "Townsfolk"
            else:  # Demon or Minion
                player_won = winning_team == "Demon"
            
            writer.writerow([
                match_id,
                player_class,
                row["username_entry"].get().strip(),
                role,
                "Win" if player_won else "Loss"
            ])

    load_full_match_history()
    reset_all()
    load_all_usernames()

def reset_all():
    global roles_generated
    script_dropdown.current(0)
    storyteller_username_var.set("")
    player_count_var.set("")
    traveler_count_var.set("0")
    for widget in player_table_frame.winfo_children():
        widget.destroy()
    player_rows.clear()
    roles_generated = False  # Reset flag
    if not create_prompt_label.winfo_ismapped():
        create_prompt_label.pack(fill='x', pady=20)
    for lbl in bluff_labels:
        lbl.config(text=lbl.cget("text").split(":")[0] + ": TBD", anchor="center")
    root.update_idletasks()

button_frame = ttk.Frame(role_tab)
button_frame.pack(pady=10)

btn_townsfolk = tk.Button(button_frame, text="Townsfolk Win", bg="#00008B", fg="white",
                         command=lambda: save_and_reset("Townsfolk"))
btn_townsfolk.grid(row=0, column=0, padx=10)

btn_demon = tk.Button(button_frame, text="Demons Win", bg="#8B0000", fg="white",
                     command=lambda: save_and_reset("Demon"))
btn_demon.grid(row=0, column=1, padx=10)

# --- Match History Tab ---
history_frame = ttk.Frame(match_tab)
history_frame.pack(fill='both', expand=True, padx=10, pady=10)

tree = ttk.Treeview(history_frame)
tree.pack(fill='both', expand=True)
tree["columns"] = ("class", "username", "role")
tree.heading("#0", text="Match")
tree.heading("class", text="Class")
tree.heading("username", text="Username")
tree.heading("role", text="Role")
tree.column("class", width=100)
tree.column("username", width=150)
tree.column("role", width=150)

def load_full_match_history():
    if not os.path.exists(MATCH_HISTORY_FILE):
        return
    for row in tree.get_children():
        tree.delete(row)

    matches = {}
    with open(MATCH_HISTORY_FILE, newline="") as f:
        reader = list(csv.reader(f))
        reader.reverse()  # newest first

        for r in reader:
            match_id = r[0]
            parts = match_id.split("|")
            
            if len(parts) == 4:  # New format
                game_id, winner, storyteller, script = parts
            else:
                continue  # Skip malformed entries
                
            if match_id not in matches:
                matches[match_id] = []
            
            # New format: match_id, class, username, role, result
            if len(r) >= 5:  # Has result field
                matches[match_id].append(r[1:5])  # class, username, role, result
            else:  # Old format without result
                matches[match_id].append(r[1:4] + ["Win" if is_team_winner(r[1], winner) else "Loss"])

    # Define colors
    townsfolk_win_color = "#00008B"  # Dark blue for town wins
    demon_win_color = "#8B0000"     # Dark red for demon wins
    win_color = "#90EE90"  # Light green for wins
    loss_color = "#FFCCCB"  # Light red for losses
    text_color = "black"    # Black text for all

    for match_id, entries in matches.items():
        parts = match_id.split("|")
        game_id, winner, storyteller, script = parts
        
        # Parent row uses dark team colors
        parent_tag = "townsfolk_win" if winner == "Townsfolk" else "demon_win"
        parent = tree.insert(
            "", "end",
            text=f"Game {game_id} | Winner: {winner} | Storyteller: {storyteller} | Script: {script}",
            open=False,
            tags=(parent_tag,)
        )
        
        for entry in entries:
            class_, username, role, result = entry
            # Child rows use win/loss colors
            tag = f"{result.lower()}"  # Just 'win' or 'loss' tag
            tree.insert(
                parent, "end", 
                values=(class_, username, role),
                tags=(tag,)
            )

    # Configure tag styles
    # Parent rows - dark team colors with white text
    tree.tag_configure("townsfolk_win", 
                      background=townsfolk_win_color, 
                      foreground="white")
    tree.tag_configure("demon_win", 
                      background=demon_win_color, 
                      foreground="white")
    
    # Child rows - light win/loss colors with black text
    tree.tag_configure("win", 
                      background=win_color, 
                      foreground=text_color)
    tree.tag_configure("loss", 
                      background=loss_color, 
                      foreground=text_color)

load_full_match_history()

# --- Player Search Tab ---

# Widgets for search tab
search_label = ttk.Label(search_tab, text="Search Player:")
search_label.pack(pady=(20, 5))

search_var = tk.StringVar()
search_entry = ttk.Entry(search_tab, textvariable=search_var)
search_entry.pack(pady=5, padx=20, fill='x')

autocomplete_listbox = tk.Listbox(search_tab, height=6)
autocomplete_listbox.pack(padx=20, fill='x')
autocomplete_listbox.place_forget()  # Hide initially

player_stats_frame = ttk.LabelFrame(search_tab, text="Player Stats")
player_stats_frame.pack(padx=20, pady=10, fill='x')

winrate_label = ttk.Label(player_stats_frame, text="Overall Win Rate: N/A")
winrate_label.pack(pady=5)

# Script filter
script_filter_var = tk.StringVar()
script_filter_dropdown = ttk.Combobox(player_stats_frame, textvariable=script_filter_var, state="readonly")
script_filter_dropdown['values'] = ['All'] + list(scripts.keys())
script_filter_dropdown.current(0)
script_filter_dropdown.pack(pady=5)

script_winrate_label = ttk.Label(player_stats_frame, text="Win Rate for Selected Script: N/A")
script_winrate_label.pack(pady=5)

# Per-role win rate frame
role_stats_frame = ttk.LabelFrame(player_stats_frame, text="Role Win Rates for Selected Script")
role_stats_frame.pack(pady=10, fill="both", expand=True)

role_stats_text = tk.Text(role_stats_frame, height=10, width=50, state="disabled")
role_stats_text.pack(padx=5, pady=5)

# Data caches
all_usernames = set()
match_data = []  # will hold all rows as dicts for search

def load_all_usernames():
    global all_usernames, match_data
    all_usernames.clear()
    match_data.clear()
    if not os.path.exists(MATCH_HISTORY_FILE):
        return
    with open(MATCH_HISTORY_FILE, newline="") as f:
        reader = csv.reader(f)
        for r in reader:
            match_id = r[0]
            parts = match_id.split("|")
            
            if len(parts) == 4:  # New format
                game_id, winner, storyteller, script = parts
            else:
                continue  # Skip malformed entries
                
            # New format: match_id, class, username, role, result
            if len(r) >= 5:
                result = r[4]
            else:  # Old format without result
                result = "Win" if is_team_winner(r[1], winner) else "Loss"
                
            cls, username, role = r[1], r[2], r[3]
            all_usernames.add(username)
            match_data.append({
                "game_id": game_id,
                "winner": winner,
                "storyteller": storyteller,
                "script": script,
                "class": cls,
                "username": username,
                "role": role,
                "result": result
            })

def update_autocomplete_list(event=None):
    typed = search_var.get().lower()
    matches = [u for u in all_usernames if typed in u.lower()]
    if matches and typed:
        autocomplete_listbox.delete(0, tk.END)
        for u in matches[:10]:
            autocomplete_listbox.insert(tk.END, u)
        autocomplete_listbox.place(x=search_entry.winfo_x(), y=search_entry.winfo_y() + search_entry.winfo_height())
        autocomplete_listbox.lift()
    else:
        autocomplete_listbox.place_forget()

def on_autocomplete_select(event):
    if not autocomplete_listbox.curselection():
        return
    selected = autocomplete_listbox.get(autocomplete_listbox.curselection())
    search_var.set(selected)
    autocomplete_listbox.place_forget()
    display_player_stats(selected)
    script_filter_var.set('All')
    script_winrate_label.config(text="Win Rate for Selected Script: N/A")

def display_player_stats(username):
    user_matches = [m for m in match_data if m["username"] == username]
    if not user_matches:
        winrate_label.config(text=f"Overall Win Rate for {username}: N/A")
        script_winrate_label.config(text="Win Rate for Selected Script: N/A")
        role_stats_text.config(state="normal")
        role_stats_text.delete(1.0, tk.END)
        role_stats_text.insert(tk.END, "No data for this player.")
        role_stats_text.config(state="disabled")
        return

    # Overall win rate (using result field)
    wins = sum(1 for m in user_matches if m["result"] == "Win")
    total = len(user_matches)
    rate = wins / total * 100
    winrate_label.config(text=f"Overall Win Rate for {username}: {rate:.2f}% ({wins}/{total})")

    # Update script-specific stats
    update_script_winrate(username)

def update_script_winrate(username=None):
    if username is None:
        username = search_var.get()
    selected_script = script_filter_var.get()
    user_matches = [m for m in match_data if m["username"] == username]

    if selected_script != "All":
        user_matches = [m for m in user_matches if m["script"] == selected_script]

    if not user_matches:
        script_winrate_label.config(text="Win Rate for Selected Script: N/A")
        role_stats_text.config(state="normal")
        role_stats_text.delete(1.0, tk.END)
        role_stats_text.insert(tk.END, "No matches for this script.")
        role_stats_text.config(state="disabled")
        return

    # Win rate for selected script (using result field)
    wins = sum(1 for m in user_matches if m["result"] == "Win")
    total = len(user_matches)
    rate = wins / total * 100
    script_winrate_label.config(text=f"Win Rate for Selected Script: {rate:.2f}% ({wins}/{total})")

    # Per-role win rate stats
    role_stats = {}
    for m in user_matches:
        role = m["role"]
        if role not in role_stats:
            role_stats[role] = {"wins": 0, "total": 0}
        role_stats[role]["total"] += 1
        if m["result"] == "Win":
            role_stats[role]["wins"] += 1

    # Display role stats
    role_stats_text.config(state="normal")
    role_stats_text.delete(1.0, tk.END)
    for role, stats in sorted(role_stats.items()):
        role_winrate = (stats["wins"] / stats["total"]) * 100
        role_stats_text.insert(tk.END, f"{role}: {role_winrate:.2f}% ({stats['wins']}/{stats['total']})\n")
    role_stats_text.config(state="disabled")

def update_script_winrate(username=None):
    if username is None:
        username = search_var.get()
    selected_script = script_filter_var.get()
    user_matches = [m for m in match_data if m["username"] == username]

    if selected_script != "All":
        user_matches = [m for m in user_matches if m["script"] == selected_script]

    if not user_matches:
        script_winrate_label.config(text="Win Rate for Selected Script: N/A")
        role_stats_text.config(state="normal")
        role_stats_text.delete(1.0, tk.END)
        role_stats_text.insert(tk.END, "No matches for this script.")
        role_stats_text.config(state="disabled")
        return

    # Win rate for selected script (team-based)
    wins = sum(1 for m in user_matches if is_team_winner(m["class"], m["winner"]))
    total = len(user_matches)
    rate = wins / total * 100
    script_winrate_label.config(text=f"Win Rate for Selected Script: {rate:.2f}% ({wins}/{total})")

    # Per-role win rate stats
    role_stats = {}
    for m in user_matches:
        role = m["role"]
        if role not in role_stats:
            role_stats[role] = {"wins": 0, "total": 0}
        role_stats[role]["total"] += 1
        if is_team_winner(m["class"], m["winner"]):
            role_stats[role]["wins"] += 1

    # Display role stats
    role_stats_text.config(state="normal")
    role_stats_text.delete(1.0, tk.END)
    for role, stats in sorted(role_stats.items()):
        role_winrate = (stats["wins"] / stats["total"]) * 100
        role_stats_text.insert(tk.END, f"{role}: {role_winrate:.2f}% ({stats['wins']}/{stats['total']})\n")
    role_stats_text.config(state="disabled")

def is_team_winner(player_class, winning_team):
    """Check if a player's class is on the winning team"""
    if winning_team == "Townsfolk":
        return player_class in ["Townsfolk", "Outsider"]
    elif winning_team == "Demon":
        return player_class in ["Demon", "Minion"]
    return False

search_entry.bind("<KeyRelease>", update_autocomplete_list)
autocomplete_listbox.bind("<<ListboxSelect>>", on_autocomplete_select)
script_filter_dropdown.bind("<<ComboboxSelected>>", lambda e: update_script_winrate())

load_all_usernames()

root.mainloop()
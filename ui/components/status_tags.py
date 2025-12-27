import tkinter as tk
from typing import Set
from config.constants import STATUS_OPTIONS

class StatusTagWidget(tk.Frame):
    """Widget for managing status tags on a player"""
    
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")
        
        self.active_tags: Set[str] = set()
        
        # Container for tag squares
        self.tag_container = tk.Frame(self)
        self.tag_container.pack(expand=True, fill="both")
        
        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self._build_menu()
        
        # Bindings
        self.bind("<Button-3>", self._show_menu)
        self.tag_container.bind("<Button-3>", self._show_menu)
        self.bind("<Enter>", lambda _: self.config(relief="groove"))
        self.bind("<Leave>", lambda _: self.config(relief="solid"))
    
    def _build_menu(self):
        """Build the context menu"""
        for status, colors in STATUS_OPTIONS.items():
            self.menu.add_command(
                label=f"\u25A0 {status}",
                command=lambda s=status: self.toggle_status(s),
                foreground=colors["bg"]
            )
        
        self.menu.add_separator()
        self.menu.add_command(
            label="Clear all statuses",
            command=self.clear_all
        )
    
    def _show_menu(self, event):
        """Show the context menu"""
        self._update_menu_checks()
        self.menu.post(event.x_root, event.y_root)
    
    def _update_menu_checks(self):
        """Update checkmarks in menu"""
        for i, (status, colors) in enumerate(STATUS_OPTIONS.items()):
            checked = status in self.active_tags
            check = "✓ " if checked else ""
            self.menu.entryconfig(i, label=f"{check}\u25A0 {status}")
    
    def toggle_status(self, status: str):
        """Toggle a status tag"""
        if status in self.active_tags:
            self.active_tags.remove(status)
        else:
            self.active_tags.add(status)
        self._update_display()
    
    def clear_all(self):
        """Clear all status tags"""
        self.active_tags.clear()
        self._update_display()
    
    def _update_display(self):
        """Update the visual display of tags"""
        # Clear existing
        for widget in self.tag_container.winfo_children():
            widget.destroy()
        
        # Create tag squares
        for status in self.active_tags:
            colors = STATUS_OPTIONS.get(status, {"bg": "#CCCCCC", "fg": "black"})
            square = tk.Label(
                self.tag_container,
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
            square.bind("<Button-3>", self._show_menu)
    
    def get_active_tags(self) -> Set[str]:
        """Get the set of active tags"""
        return self.active_tags.copy()
    
    def grid(self, **kwargs):
        """Override grid to position the frame"""
        super().grid(**kwargs)
        self.grid_propagate(True)
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileTreeView(ttk.Treeview):
    def __init__(self, master, scanner, token_counter, **kwargs):
        super().__init__(master, style="Custom.Treeview", show="tree headings", 
                        selectmode="none", **kwargs)
        
        self.scanner = scanner
        self.token_counter = token_counter
        self._checkboxes: Dict[str, tk.BooleanVar] = {}
        
        # Configure Windows style
        style = ttk.Style()
        style.configure("Custom.Treeview",
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       indent=30,
                       rowheight=30)
        
        # Disable the expand/collapse button
        style.layout("Custom.Treeview", [
            ('Custom.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Configure selection colors
        style.map("Custom.Treeview",
                 background=[("selected", "#CCE8FF")],
                 foreground=[("selected", "black")])
        
        # Configure tags with Windows colors
        self.tag_configure('selected', foreground='#0078D4')
        self.tag_configure('folder', foreground='#0078D4')
        self.tag_configure('file', foreground='black')
        self.tag_configure('checkbox_selected', image='')
        self.tag_configure('checkbox_unselected', image='')
        self.tag_configure('token_count', foreground='#666666')
        
        # Add columns
        self["columns"] = ("fullpath", "tokens")
        self.column("fullpath", width=0, stretch=False)
        self.column("tokens", width=150, stretch=False)
        self.heading("#0", text="", anchor="w")
        self.heading("fullpath", text="", anchor="w")
        self.heading("tokens", text="", anchor="e")
        
        # Create checkbox images
        self._create_checkbox_images()
        
        # Bind events
        self.bind('<Button-1>', self._on_click)
        self.bind('<Motion>', self._on_motion)
        
        logger.debug("FileTreeView initialized with Windows styling")

    def _create_checkbox_images(self):
        """Create Windows-style checkbox images."""
        # Selected checkbox (larger)
        selected = tk.PhotoImage(width=24, height=24)
        selected.put(('#0078D4',), to=(4, 4, 19, 19))  # Blue fill
        selected.put(('white',), to=(7, 10, 16, 13))  # Checkmark
        
        # Unselected checkbox (larger)
        unselected = tk.PhotoImage(width=24, height=24)
        unselected.put(('#666666',), to=(4, 4, 19, 4))  # Top
        unselected.put(('#666666',), to=(4, 19, 19, 19))  # Bottom
        unselected.put(('#666666',), to=(4, 4, 4, 19))  # Left
        unselected.put(('#666666',), to=(19, 4, 19, 19))  # Right
        
        self._icons = {
            'selected': selected,
            'unselected': unselected
        }
        
        # Update tag configurations with images
        self.tag_configure('checkbox_selected', image=selected)
        self.tag_configure('checkbox_unselected', image=unselected)
        
        logger.debug("Created Windows-style checkbox images")

    def _create_checkbox(self, item_id, initial_state=False):
        """Create a checkbox variable for an item."""
        var = tk.BooleanVar(value=initial_state)
        var.trace_add('write', lambda *args: self._on_checkbox_change(item_id))
        self._checkboxes[item_id] = var
        logger.debug(f"Created checkbox for item {item_id} with initial state: {initial_state}")
        return var

    def _on_click(self, event):
        """Handle click events on the tree."""
        item_id = self.identify_row(event.y)
        if not item_id:
            return
        
        # Get x coordinate for checkbox region
        x_coord = event.x
        
        # Calculate checkbox region (assuming it's within first 24 pixels)
        checkbox_region = x_coord <= 24
        
        # Only toggle checkbox if clicked in checkbox region
        if checkbox_region and item_id in self._checkboxes:
            current_state = self._checkboxes[item_id].get()
            new_state = not current_state
            self._checkboxes[item_id].set(new_state)
            
        # Always keep items expanded
        self.item(item_id, open=True)

    def _on_motion(self, event):
        """Handle mouse motion events."""
        item_id = self.identify_row(event.y)
        if item_id:
            self.selection_set(item_id)
        else:
            self.selection_remove(self.selection())

    def _on_checkbox_change(self, item_id):
        """Handle checkbox state changes."""
        if not item_id in self._checkboxes:
            return
            
        is_selected = self._checkboxes[item_id].get()
        
        # Update item appearance
        self._update_item_appearance(item_id, is_selected)
        
        # Update children states first
        for child in self.get_children(item_id):
            if child in self._checkboxes:
                self._checkboxes[child].set(is_selected)
                self._update_item_appearance(child, is_selected)
        
        # Update parent state last
        parent_id = self.parent(item_id)
        if parent_id:
            self._update_parent_state(parent_id)

    def _update_item_appearance(self, item_id: str, is_selected: bool):
        """Update the appearance of an item based on selection state."""
        # Get existing tags but filter out checkbox-related ones
        current_tags = [tag for tag in self.item(item_id)["tags"] 
                       if tag not in ('checkbox_selected', 'checkbox_unselected', 'selected')]
        
        # Add appropriate checkbox tag
        current_tags.append('checkbox_selected' if is_selected else 'checkbox_unselected')
        
        # Add selected tag if needed
        if is_selected:
            current_tags.append('selected')
            
        # Update the item's tags
        self.item(item_id, tags=current_tags)

    def _update_parent_state(self, parent_id: str):
        """Update parent checkbox state based on children."""
        if not parent_id or parent_id not in self._checkboxes:
            return
            
        children = self.get_children(parent_id)
        if not children:
            return
            
        # Check if all children are selected
        all_selected = all(
            self._checkboxes[child].get() 
            for child in children 
            if child in self._checkboxes
        )
        
        logger.debug(f"Updating parent {parent_id} state - All children selected: {all_selected}")
        self._checkboxes[parent_id].set(all_selected)
        self._update_item_appearance(parent_id, all_selected)

    def insert_with_tokens(self, parent, index, text, **kwargs):
        """Insert an item with token count."""
        item_id = self.insert(parent, index, text=text, **kwargs)
        
        # Always set item as expanded
        self.item(item_id, open=True)
        
        # Get full path
        full_path = kwargs.get('values', [''])[0]
        
        # Calculate and display token count
        if os.path.isfile(full_path):
            token_str, percentage = self.token_counter.get_file_stats(full_path)
            self.set(item_id, "tokens", f"{token_str} ({percentage:.1f}%)")
        elif os.path.isdir(full_path):
            token_str, percentage = self.token_counter.get_dir_stats(full_path)
            self.set(item_id, "tokens", f"{token_str} ({percentage:.1f}%)")
            
        return item_id
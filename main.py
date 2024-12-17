import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import our components
from src.ui.components.file_tree import FileTreeView
from src.core.token_counter import TokenCounter

class RepoPromptApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Repo Prompt")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.token_counter = TokenCounter()
        self.setup_ui()
        
        # File tracking
        self.current_project = None
        self.checked_items = set()
        
        # Checkbox symbols
        self.CHECKED = "☑ "
        self.UNCHECKED = "☐ "
        
        # Ignore patterns
        self.ignore_patterns = {
            'node_modules',
            'vendor',
            'storage',
            'bootstrap/cache',
            '.git',
            '.env'
        }
        
    def setup_ui(self):
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project...", command=self.select_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Top frame for project selection and total tokens
        top_frame = ctk.CTkFrame(self.root)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Project selection button
        select_btn = ctk.CTkButton(top_frame, text="Select Project", 
                                command=self.select_project)
        select_btn.grid(row=0, column=0, padx=(0,10))
        
        # Total tokens label
        self.total_tokens_label = ctk.CTkLabel(top_frame, text="Total Tokens: 0", 
                                           font=("Segoe UI", 12))
        self.total_tokens_label.grid(row=0, column=1, sticky="e")
        
        # Left panel - Tree view
        tree_frame = ctk.CTkFrame(self.root)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Create tree with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        
        self.tree = FileTreeView(tree_frame, None, self.token_counter)
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Bind click event
        self.tree.bind('<Button-1>', self.on_click)
        
        # Connect scrollbar
        tree_scroll.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=tree_scroll.set)
        
        # Right panel - Text view
        text_frame = ctk.CTkFrame(self.root)
        text_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0,10))
        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        title_label = ctk.CTkLabel(text_frame, text="File Tree", 
                                font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Text editor with scrollbar
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.grid(row=1, column=1, sticky="ns")
        
        self.file_tree_text = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 10),
                                   bg="white", fg="black")
        self.file_tree_text.grid(row=1, column=0, sticky="nsew")
        
        # Connect scrollbar
        text_scroll.config(command=self.file_tree_text.yview)
        self.file_tree_text.config(yscrollcommand=text_scroll.set)
        
    def on_click(self, event):
        """Handle click events on the tree."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        # Get click region
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "tree":
            # Only toggle checkbox
            self.toggle_check(item_id)
        elif region == "button":
            # Just toggle expansion without affecting checkbox
            current_state = self.tree.item(item_id, "open")
            item_text = self.tree.item(item_id)['text']
            item_name = item_text[2:] if item_text.startswith((self.CHECKED, self.UNCHECKED)) else item_text
            logger.debug(f"{'Collapsing' if current_state else 'Expanding'} folder: {item_name}")
            
            self.tree.item(item_id, open=not current_state)
            
            # Ensure checkbox state is preserved
            is_checked = item_id in self.checked_items
            new_text = (self.CHECKED if is_checked else self.UNCHECKED) + item_text[2:]
            self.tree.item(item_id, text=new_text)
            
            # Ensure children's checkbox states are preserved
            for child in self.tree.get_children(item_id):
                self.preserve_checkbox_state(child)
                
    def preserve_checkbox_state(self, item_id):
        """Preserve the checkbox state of an item and its children."""
        current_text = self.tree.item(item_id)['text']
        is_checked = item_id in self.checked_items
        new_text = (self.CHECKED if is_checked else self.UNCHECKED) + current_text[2:]
        self.tree.item(item_id, text=new_text)
        
        for child in self.tree.get_children(item_id):
            self.preserve_checkbox_state(child)
            
    def toggle_check(self, item_id):
        """Toggle checkbox state for an item and its children."""
        current_text = self.tree.item(item_id)['text']
        item_name = current_text[2:] if current_text.startswith((self.CHECKED, self.UNCHECKED)) else current_text
        
        if current_text.startswith(self.CHECKED):
            logger.debug(f"Unchecking: {item_name}")
            new_text = self.UNCHECKED + item_name
            self.checked_items.discard(item_id)
        else:
            logger.debug(f"Checking: {item_name}")
            new_text = self.CHECKED + item_name
            self.checked_items.add(item_id)
            
        self.tree.item(item_id, text=new_text)
        
        # Toggle children
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, new_text.startswith(self.CHECKED))
        
        # Update the file tree text
        self.update_file_tree_text()
        
    def toggle_children(self, item_id, checked):
        """Toggle checkbox state of children without affecting expansion state."""
        current_text = self.tree.item(item_id)['text']
        item_name = current_text[2:] if current_text.startswith((self.CHECKED, self.UNCHECKED)) else current_text
        new_text = (self.CHECKED if checked else self.UNCHECKED) + item_name
        
        logger.debug(f"{'Checking' if checked else 'Unchecking'} child: {item_name}")
        self.tree.item(item_id, text=new_text)
        
        if checked:
            self.checked_items.add(item_id)
        else:
            self.checked_items.discard(item_id)
            
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, checked)
            
    def update_file_tree_text(self):
        # Clear text editor
        self.file_tree_text.delete('1.0', tk.END)
        
        # Get all items and their structure
        tree_items = []
        
        def collect_items(node, level=0, is_last_sibling=False, parent_prefix=""):
            # Check if item is in checked_items set
            if node in self.checked_items:
                item_text = self.tree.item(node)['text']
                clean_text = item_text[2:] if item_text.startswith((self.CHECKED, self.UNCHECKED)) else item_text
                tree_items.append((level, clean_text, parent_prefix))
            
                # Process children if parent is checked
                children = self.tree.get_children(node)
                for i, child in enumerate(children):
                    is_last = i == len(children) - 1
                    
                    # Calculate the new parent prefix for the child's children
                    new_parent_prefix = parent_prefix
                    if level > 0:  # Skip for root level
                        new_parent_prefix = parent_prefix + ("    " if is_last else "│   ")
                    
                    collect_items(child, level + 1, is_last, new_parent_prefix)
        
        # Collect all items starting from root
        for item in self.tree.get_children():
            collect_items(item)
            
        # Generate tree text
        # First, add the root item without indentation
        if tree_items:
            root_text = tree_items[0][1]
            self.file_tree_text.insert(tk.END, f"{root_text}/\n")
            
            # Then add all other items with tree structure
            current_level = 0
            for level, text, prefix in tree_items[1:]:  # Skip the root item
                # Check if item is a directory
                is_dir = bool(self.tree.get_children(self.get_item_by_text(text)))
                
                # Format text based on whether it's a directory or file
                if is_dir:
                    text_with_slash = f"{text}/"
                    if level == 1:
                        line = f"│   {text_with_slash}\n"
                    else:
                        if prefix.endswith("    "):  # Last item in its group
                            line = f"{prefix[:-4]}{text_with_slash}\n"
                        else:
                            line = f"{prefix}{text_with_slash}\n"
                else:
                    # Files get the ├── prefix
                    if level == 1:
                        line = f"│   ├── {text}\n"
                    else:
                        if prefix.endswith("    "):  # Last item in its group
                            line = f"{prefix[:-4]}├── {text}\n"
                        else:
                            line = f"{prefix}├── {text}\n"
                
                current_level = level
                self.file_tree_text.insert(tk.END, line)
        
    def get_item_by_text(self, text):
        """Helper function to find a tree item by its text"""
        def find_item(node):
            item_text = self.tree.item(node)['text']
            clean_text = item_text[2:] if item_text.startswith((self.CHECKED, self.UNCHECKED)) else item_text
            if clean_text == text:
                return node
            for child in self.tree.get_children(node):
                result = find_item(child)
                if result:
                    return result
            return None
            
        for item in self.tree.get_children():
            result = find_item(item)
            if result:
                return result
        return None
        
    def get_full_path(self, item):
        path_parts = []
        while item:
            text = self.tree.item(item)['text']
            if text.startswith((self.CHECKED, self.UNCHECKED)):
                text = text[2:]
            path_parts.insert(0, text)
            item = self.tree.parent(item)
        return os.path.join(*path_parts)
        
    def select_project(self):
        """Open a directory selection dialog and load the project."""
        logger.debug("Selecting project directory...")
        directory = filedialog.askdirectory()
        if directory:
            self.current_project = directory
            logger.debug(f"Selected project directory: {directory}")
            
            # Load project tree
            logger.debug(f"Loading project tree from: {directory}")
            self.load_project_tree(directory)
            
            # Update total tokens label
            if self.token_counter.total_tokens >= 1000:
                total_str = f"{self.token_counter.total_tokens/1000:.1f}k"
            else:
                total_str = str(self.token_counter.total_tokens)
            self.total_tokens_label.configure(text=f"Total Tokens: {total_str}")
            
            # Expand all nodes after loading
            self.expand_all_nodes()
            
            # Update the text view
            self.update_file_tree_text()
            
    def expand_all_nodes(self):
        def expand_node(node):
            self.tree.item(node, open=True)
            for child in self.tree.get_children(node):
                expand_node(child)
                
        for node in self.tree.get_children():
            expand_node(node)
            
    def load_project_tree(self, path):
        debug_print(f"Loading project tree from: {path}")
        self.checked_items.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Calculate total tokens for the project
        debug_print("Calculating total tokens...")
        self.token_counter.update_total_tokens(path)
            
        debug_print("Adding tree nodes...")
        self.add_tree_nodes("", path)
        debug_print(f"Added {len(self.checked_items)} items to tree")
        
    def should_include_file(self, name, is_dir):
        if name in self.ignore_patterns:
            return False
        if name.startswith('.'):
            return False
        if not is_dir and not name.endswith('.php'):
            return False
        return True
        
    def add_tree_nodes(self, parent, path):
        debug_print(f"Processing directory: {path}")
        basename = os.path.basename(path) or path
        
        # Use insert_with_tokens instead of insert
        node = self.tree.insert_with_tokens(parent, "end", 
                                        text=f"{self.CHECKED}{basename}",
                                        values=[path])
        self.checked_items.add(node)
        
        try:
            items = sorted(os.listdir(path))
            debug_print(f"Found {len(items)} items in {path}")
            
            for item in items:
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                if not self.should_include_file(item, is_dir):
                    debug_print(f"Skipping excluded item: {item}")
                    continue
                    
                if is_dir:
                    self.add_tree_nodes(node, item_path)
                else:
                    debug_print(f"Adding file: {item}")
                    child = self.tree.insert_with_tokens(node, "end", 
                                                     text=f"{self.CHECKED}{item}",
                                                     values=[item_path])
                    self.checked_items.add(child)
                    
        except PermissionError as e:
            debug_print(f"Permission error accessing {path}: {str(e)}")
            pass
            
def debug_print(msg):
    logger.debug(msg)
    
if __name__ == "__main__":
    app = RepoPromptApp()
    app.root.mainloop() 
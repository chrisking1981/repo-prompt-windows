import tkinter as tk
from tkinter import ttk, filedialog
import os

def debug_print(message):
    print(f"DEBUG: {message}")

class RepoPromptApp:
    def __init__(self, root):
        debug_print("Initializing RepoPromptApp")
        self.root = root
        self.root.title("Repo Prompt")
        self.root.geometry("1200x800")

        # Initialize tracking variables
        self.checked_items = set()

        # Set theme colors
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'secondary': '#313244',
            'hover': '#45475a',
            'selected': '#89b4fa20',
            'button': '#89b4fa',
            'button_text': '#1e1e2e'
        }

        # Define checkbox symbols
        self.CHECKED = "☒ "
        self.UNCHECKED = "☐ "

        debug_print("Setting up UI components")
        # Configure root window
        self.root.configure(bg=self.colors['bg'])

        # Configure styles
        self.setup_styles()

        # Create main split pane
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL, style='Custom.TPanedwindow')
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Setup frames
        self.setup_left_frame()
        self.setup_right_frame()

        # Bind events
        self.tree.bind('<Button-1>', self.on_click)

        # Files to ignore
        self.ignore_patterns = [
            '.git', 'vendor', 'node_modules', 'storage', 'public',
            'bootstrap/cache', 'tests', '.env', '.gitignore',
            'package.json', 'composer.json', 'composer.lock',
            'webpack.mix.js', 'package-lock.json', 'phpunit.xml',
            'README.md', 'server.php', 'artisan'
        ]
        debug_print("Initialization complete")

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure custom styles
        style.configure(
            'Custom.Treeview',
            background=self.colors['secondary'],
            foreground=self.colors['fg'],
            fieldbackground=self.colors['secondary'],
            indent=20,
            rowheight=30,
            font=('Segoe UI', 11)
        )
        
        # Remove borders
        style.layout('Custom.Treeview', [
            ('Custom.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Button styles
        style.configure(
            'Accent.TButton',
            background=self.colors['accent'],
            foreground=self.colors['button_text'],
            padding=10,
            font=('Segoe UI', 10, 'bold')
        )
        
        # Frame styles
        style.configure(
            'Custom.TFrame',
            background=self.colors['bg']
        )
        
        # PanedWindow styles
        style.configure(
            'Custom.TPanedwindow',
            background=self.colors['bg']
        )
        
        # Label styles
        style.configure(
            'Header.TLabel',
            background=self.colors['bg'],
            foreground=self.colors['accent'],
            font=('Segoe UI', 12, 'bold')
        )

    def setup_left_frame(self):
        debug_print("Setting up left frame")
        # Left frame
        self.left_frame = ttk.Frame(self.paned, style='Custom.TFrame')
        self.paned.add(self.left_frame, weight=1)

        # Header frame for project selection
        self.header_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
        self.header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Project selection button
        self.select_btn = ttk.Button(
            self.header_frame,
            text="Select Laravel Project",
            command=self.select_project,
            style='Accent.TButton'
        )
        self.select_btn.pack(fill=tk.X, padx=5, pady=5)

        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview setup
        self.tree = ttk.Treeview(
            tree_frame,
            selectmode="none",
            style="Custom.Treeview"
        )
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout for treeview and scrollbars
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')

        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Configure tree columns
        self.tree["columns"] = ("fullpath",)
        self.tree.column("#0", width=450)
        self.tree.column("fullpath", width=0, stretch=False)
        self.tree.heading("#0", text="")
        self.tree.heading("fullpath", text="")

        debug_print("Left frame setup complete")

    def setup_right_frame(self):
        debug_print("Setting up right frame")
        # Right frame
        self.right_frame = ttk.Frame(self.paned, style='Custom.TFrame')
        self.paned.add(self.right_frame, weight=2)
        
        # File Tree label
        self.tree_label = ttk.Label(
            self.right_frame,
            text="File Tree",
            style='Header.TLabel'
        )
        self.tree_label.pack(anchor='w', padx=10, pady=(5,5))

        # Text editor for file tree
        self.file_tree_text = tk.Text(
            self.right_frame,
            wrap=tk.NONE,
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['bg'],
            relief='flat',
            font=('Consolas', 11),
            height=20
        )
        self.file_tree_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbars for text editor
        self.tree_vsb = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.file_tree_text.yview)
        self.tree_hsb = ttk.Scrollbar(self.right_frame, orient="horizontal", command=self.file_tree_text.xview)
        self.file_tree_text.configure(yscrollcommand=self.tree_vsb.set, xscrollcommand=self.tree_hsb.set)

        # Pack scrollbars
        self.tree_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_hsb.pack(side=tk.BOTTOM, fill=tk.X)

        debug_print("Right frame setup complete")

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "tree":
            self.toggle_check(item_id)
            return

    def toggle_check(self, item_id):
        debug_print("\n=== Toggle Checkbox ===")
        current_text = self.tree.item(item_id)['text']
        item_name = current_text[2:] if current_text.startswith((self.CHECKED, self.UNCHECKED)) else current_text
        
        if current_text.startswith(self.CHECKED):
            debug_print(f"Unchecking item: {item_name}")
            new_text = self.UNCHECKED + item_name
            self.checked_items.discard(item_id)
        else:
            debug_print(f"Checking item: {item_name}")
            new_text = self.CHECKED + item_name
            self.checked_items.add(item_id)
            
        self.tree.item(item_id, text=new_text)
        
        # Toggle children
        debug_print(f"Processing children of: {item_name}")
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, new_text.startswith(self.CHECKED))
        
        # Update the file tree text
        debug_print("Triggering file tree text update...")
        self.update_file_tree_text()
        debug_print("=== Toggle Complete ===\n")

    def toggle_children(self, item_id, checked):
        current_text = self.tree.item(item_id)['text']
        item_name = current_text[2:] if current_text.startswith((self.CHECKED, self.UNCHECKED)) else current_text
        new_text = (self.CHECKED if checked else self.UNCHECKED) + item_name
        
        debug_print(f"{'Checking' if checked else 'Unchecking'} child: {item_name}")
        self.tree.item(item_id, text=new_text)
        
        if checked:
            self.checked_items.add(item_id)
        else:
            self.checked_items.discard(item_id)
            
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, checked)

    def update_file_tree_text(self):
        debug_print("\n=== Updating File Tree Text Area ===")
        
        # Clear text editor
        self.file_tree_text.delete('1.0', tk.END)
        debug_print("Cleared text area")

        # Get all items and their structure
        tree_items = []
        debug_print("Collecting checked items for tree view...")
        
        def collect_items(node, level=0, is_last_sibling=False, parent_prefix=""):
            item_text = self.tree.item(node)['text']
            if item_text.startswith(self.CHECKED):  # Only include checked items
                # Remove checkbox from text
                clean_text = item_text[2:] if item_text.startswith((self.CHECKED, self.UNCHECKED)) else item_text
                tree_items.append((level, clean_text, parent_prefix))
                debug_print(f"Added item: {parent_prefix}{clean_text}")
            
            # Process children
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
        debug_print("\nGenerating tree text structure...")
        
        # First, add the root item without indentation
        if tree_items:
            root_text = tree_items[0][1]
            self.file_tree_text.insert(tk.END, f"{root_text}/\n")
            debug_print(f"Added root: {root_text}")

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
                debug_print(f"Added line: {line.strip()}")

        debug_print("=== File Tree Text Area Update Complete ===\n")

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
        debug_print("Selecting project directory...")
        folder = filedialog.askdirectory(title="Select Laravel Project")
        if folder:
            debug_print(f"Selected project directory: {folder}")
            self.load_project_tree(folder)
            debug_print("Expanding all nodes...")
            self.expand_all_nodes()
            debug_print("Updating file tree text...")
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
        node = self.tree.insert(parent, "end", text=f"{self.CHECKED}{basename}")
        self.checked_items.add(node)
        
        full_path = os.path.join(parent, basename) if parent else basename
        self.tree.set(node, "fullpath", full_path)

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
                    child = self.tree.insert(node, "end", text=f"{self.CHECKED}{item}")
                    self.checked_items.add(child)
                    full_child_path = os.path.join(full_path, item)
                    self.tree.set(child, "fullpath", full_child_path)

        except PermissionError as e:
            debug_print(f"Permission error accessing {path}: {str(e)}")
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RepoPromptApp(root)
    root.mainloop() 
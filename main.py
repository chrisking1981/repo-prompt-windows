import tkinter as tk
from tkinter import ttk, filedialog
import os

class RepoPromptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Repo Prompt for Laravel")
        self.root.geometry("1200x800")

        # Create main split pane
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left frame
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=1)

        # Project selection button
        self.select_btn = ttk.Button(self.left_frame, text="Select Laravel Project", command=self.select_project)
        self.select_btn.pack(fill=tk.X, padx=5, pady=5)

        # Create style for treeview
        style = ttk.Style()
        style.configure("CustomTree.Treeview", indent=20)  # Increase indentation

        # Treeview with checkboxes
        self.tree = ttk.Treeview(self.left_frame, selectmode="none", style="CustomTree.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar to treeview
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Configure tree columns for checkbox
        self.tree["columns"] = ("fullpath",)  # Hidden column for full path
        self.tree.column("#0", width=450)  # Main column with items
        self.tree.column("fullpath", width=0, stretch=False)  # Hidden column
        self.tree.heading("#0", text="")
        self.tree.heading("fullpath", text="")

        # Right frame
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=2)
        
        # Selected files list (right panel)
        self.selected_files_label = ttk.Label(self.right_frame, text="Selected Files:")
        self.selected_files_label.pack(padx=10, pady=(10,0), anchor='w')
        
        self.selected_files_text = tk.Text(self.right_frame, wrap=tk.WORD, height=20)
        self.selected_files_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind click events
        self.tree.bind('<Button-1>', self.on_click)

        # Files to ignore for O1 Pro prompt
        self.ignore_patterns = [
            '.git', 'vendor', 'node_modules', 'storage', 'public',
            'bootstrap/cache', 'tests', '.env', '.gitignore',
            'package.json', 'composer.json', 'composer.lock',
            'webpack.mix.js', 'package-lock.json', 'phpunit.xml',
            'README.md', 'server.php', 'artisan'
        ]

        # Track checked state
        self.checked_items = set()

    def expand_all_nodes(self):
        def expand_node(node):
            self.tree.item(node, open=True)
            for child in self.tree.get_children(node):
                expand_node(child)

        # Expand all nodes starting from root
        for node in self.tree.get_children():
            expand_node(node)

    def on_click(self, event):
        # Get clicked item
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        # Get region (icon, text)
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "tree":  # Click on checkbox/name area
            self.toggle_check(item_id)
            return

    def toggle_check(self, item_id):
        # Toggle checkbox in text
        current_text = self.tree.item(item_id)['text']
        if current_text.startswith("☑ "):
            new_text = "☐ " + current_text[2:]
            self.checked_items.discard(item_id)
        else:
            new_text = "☑ " + (current_text[2:] if current_text.startswith("☐ ") else current_text)
            self.checked_items.add(item_id)
            
        self.tree.item(item_id, text=new_text)
        
        # Toggle all children
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, new_text.startswith("☑"))
        
        # Update selected files display
        self.update_selected_files()

    def toggle_children(self, item_id, checked):
        current_text = self.tree.item(item_id)['text']
        new_text = ("☑ " if checked else "☐ ") + (current_text[2:] if current_text.startswith(("☑ ", "☐ ")) else current_text)
        self.tree.item(item_id, text=new_text)
        
        if checked:
            self.checked_items.add(item_id)
        else:
            self.checked_items.discard(item_id)
            
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, checked)

    def update_selected_files(self):
        # Clear current display
        self.selected_files_text.delete('1.0', tk.END)
        
        # Get all checked items
        checked_items = []
        for item_id in self.checked_items:
            checked_items.append(self.tree.set(item_id, "fullpath"))
            
        # Update display
        for item in sorted(checked_items):
            if item:  # Only show if path exists
                self.selected_files_text.insert(tk.END, f"• {item}\n")

    def get_full_path(self, item):
        # Build the full path from root to item
        path_parts = []
        while item:
            text = self.tree.item(item)['text']
            # Remove checkbox from text
            if text.startswith(("☑ ", "☐ ")):
                text = text[2:]
            path_parts.insert(0, text)
            item = self.tree.parent(item)
        return os.path.join(*path_parts)

    def select_project(self):
        folder = filedialog.askdirectory(title="Select Laravel Project")
        if folder:
            self.load_project_tree(folder)
            # Expand all nodes after loading
            self.expand_all_nodes()
            # Update selected files display
            self.update_selected_files()

    def load_project_tree(self, path):
        # Clear existing items
        self.checked_items.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load the directory structure
        self.add_tree_nodes("", path)

    def should_include_file(self, name, is_dir):
        # Check if file/directory should be included
        if name in self.ignore_patterns:
            return False
        if name.startswith('.'):
            return False
        if not is_dir and not name.endswith('.php'):
            return False
        return True

    def add_tree_nodes(self, parent, path):
        # Add directory as a node
        basename = os.path.basename(path) or path
        node = self.tree.insert(parent, "end", text=f"☑ {basename}")
        self.checked_items.add(node)
        
        # Store full path in hidden column
        full_path = os.path.join(parent, basename) if parent else basename
        self.tree.set(node, "fullpath", full_path)

        try:
            # List directory contents
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                # Filter unwanted files/directories
                if not self.should_include_file(item, is_dir):
                    continue
                    
                if is_dir:
                    self.add_tree_nodes(node, item_path)
                else:
                    child = self.tree.insert(node, "end", text=f"☑ {item}")
                    self.checked_items.add(child)
                    self.tree.set(child, "fullpath", os.path.join(full_path, item))
        except PermissionError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RepoPromptApp(root)
    root.mainloop() 
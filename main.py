import tkinter as tk
from tkinter import ttk, filedialog
import os

class RepoPromptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Repo Prompt for Laravel")
        self.root.geometry("1200x800")

        # Set theme colors
        self.colors = {
            'bg': '#1e1e2e',           # Dark background
            'fg': '#cdd6f4',           # Light text
            'accent': '#89b4fa',       # Accent blue
            'secondary': '#313244',    # Secondary background
            'hover': '#45475a',        # Hover color
            'selected': '#89b4fa20',   # Selected with transparency
            'button': '#89b4fa',       # Button color
            'button_text': '#1e1e2e',  # Button text color
        }

        # Configure root window
        self.root.configure(bg=self.colors['bg'])

        # Configure styles
        self.setup_styles()

        # Create main split pane
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL, style='Custom.TPanedwindow')
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame
        self.left_frame = ttk.Frame(self.paned, style='Custom.TFrame')
        self.paned.add(self.left_frame, weight=1)

        # Header frame for project selection
        self.header_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
        self.header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Project selection button with modern style
        self.select_btn = ttk.Button(
            self.header_frame,
            text="Select Laravel Project",
            command=self.select_project,
            style='Accent.TButton'
        )
        self.select_btn.pack(fill=tk.X, padx=5, pady=5)

        # Treeview with modern styling
        self.tree = ttk.Treeview(
            self.left_frame,
            selectmode="none",
            style="Custom.Treeview",
            padding=5
        )
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Modern scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.left_frame,
            orient="vertical",
            command=self.tree.yview,
            style='Custom.Vertical.TScrollbar'
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Configure tree columns
        self.tree["columns"] = ("fullpath",)
        self.tree.column("#0", width=450)
        self.tree.column("fullpath", width=0, stretch=False)
        self.tree.heading("#0", text="")
        self.tree.heading("fullpath", text="")

        # Right frame
        self.right_frame = ttk.Frame(self.paned, style='Custom.TFrame')
        self.paned.add(self.right_frame, weight=2)
        
        # Selected files header with modern style
        self.selected_files_label = ttk.Label(
            self.right_frame,
            text="Selected Files",
            style='Header.TLabel'
        )
        self.selected_files_label.pack(padx=10, pady=(10,5), anchor='w')
        
        # Selected files text area with modern style
        self.selected_files_text = tk.Text(
            self.right_frame,
            wrap=tk.WORD,
            height=20,
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['bg'],
            relief='flat',
            font=('Segoe UI', 10)
        )
        self.selected_files_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        # Track checked state
        self.checked_items = set()

        # Define checkbox symbols
        self.CHECKED = "☒ "    # Bigger checked box
        self.UNCHECKED = "☐ "  # Bigger empty box
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure custom styles
        style.configure(
            'Custom.Treeview',
            background=self.colors['secondary'],
            foreground=self.colors['fg'],
            fieldbackground=self.colors['secondary'],
            indent=20,
            rowheight=30,  # Increased row height
            font=('Segoe UI', 11)  # Slightly larger font
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
        
        # Scrollbar style
        style.configure(
            'Custom.Vertical.TScrollbar',
            background=self.colors['secondary'],
            troughcolor=self.colors['bg'],
            width=10,
            arrowsize=0
        )

    def expand_all_nodes(self):
        def expand_node(node):
            self.tree.item(node, open=True)
            for child in self.tree.get_children(node):
                expand_node(child)

        for node in self.tree.get_children():
            expand_node(node)

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "tree":
            self.toggle_check(item_id)
            return

    def toggle_check(self, item_id):
        current_text = self.tree.item(item_id)['text']
        if current_text.startswith(self.CHECKED):
            new_text = self.UNCHECKED + current_text[2:]
            self.checked_items.discard(item_id)
        else:
            new_text = self.CHECKED + (current_text[2:] if current_text.startswith(self.UNCHECKED) else current_text)
            self.checked_items.add(item_id)
            
        self.tree.item(item_id, text=new_text)
        
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, new_text.startswith(self.CHECKED))
        
        self.update_selected_files()

    def toggle_children(self, item_id, checked):
        current_text = self.tree.item(item_id)['text']
        new_text = (self.CHECKED if checked else self.UNCHECKED) + (current_text[2:] if current_text.startswith((self.CHECKED, self.UNCHECKED)) else current_text)
        self.tree.item(item_id, text=new_text)
        
        if checked:
            self.checked_items.add(item_id)
        else:
            self.checked_items.discard(item_id)
            
        for child in self.tree.get_children(item_id):
            self.toggle_children(child, checked)

    def update_selected_files(self):
        self.selected_files_text.delete('1.0', tk.END)
        
        checked_items = []
        for item_id in self.checked_items:
            checked_items.append(self.tree.set(item_id, "fullpath"))
            
        for item in sorted(checked_items):
            if item:
                self.selected_files_text.insert(tk.END, f"• {item}\n")

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
        folder = filedialog.askdirectory(title="Select Laravel Project")
        if folder:
            self.load_project_tree(folder)
            self.expand_all_nodes()
            self.update_selected_files()

    def load_project_tree(self, path):
        self.checked_items.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.add_tree_nodes("", path)

    def should_include_file(self, name, is_dir):
        if name in self.ignore_patterns:
            return False
        if name.startswith('.'):
            return False
        if not is_dir and not name.endswith('.php'):
            return False
        return True

    def add_tree_nodes(self, parent, path):
        basename = os.path.basename(path) or path
        node = self.tree.insert(parent, "end", text=f"{self.CHECKED}{basename}")
        self.checked_items.add(node)
        
        full_path = os.path.join(parent, basename) if parent else basename
        self.tree.set(node, "fullpath", full_path)

        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                if not self.should_include_file(item, is_dir):
                    continue
                    
                if is_dir:
                    self.add_tree_nodes(node, item_path)
                else:
                    child = self.tree.insert(node, "end", text=f"{self.CHECKED}{item}")
                    self.checked_items.add(child)
                    self.tree.set(child, "fullpath", os.path.join(full_path, item))
        except PermissionError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RepoPromptApp(root)
    root.mainloop() 
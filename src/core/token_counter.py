import os
import tiktoken
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class TokenCounter:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.cache: Dict[str, int] = {}
        self.total_tokens = 0
        
        # File extensions to skip
        self.skip_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.node', '.bin', 
            '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
            '.woff', '.woff2', '.ttf', '.eot', '.css', '.js',
            '.json', '.lock', '.md', '.xml', '.yml', '.yaml'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git', 'node_modules', 'vendor', 'storage',
            'bootstrap/cache', 'public/build'
        }
        
    def should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped."""
        # Skip by extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in self.skip_extensions:
            return True
            
        # Skip by directory
        path_parts = file_path.replace('\\', '/').split('/')
        for part in path_parts:
            if part in self.skip_dirs:
                return True
                
        return False
        
    def is_binary_file(self, file_path: str) -> bool:
        """Check if file appears to be binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk  # Binary files typically contain null bytes
        except Exception:
            return True
            
    def count_file_tokens(self, file_path: str) -> int:
        """Count tokens in a file."""
        if file_path in self.cache:
            return self.cache[file_path]
            
        if self.should_skip_file(file_path) or self.is_binary_file(file_path):
            logger.debug(f"Skipping binary/excluded file: {file_path}")
            self.cache[file_path] = 0
            return 0
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                token_count = len(self.encoder.encode(content))
                self.cache[file_path] = token_count
                return token_count
        except Exception as e:
            logger.debug(f"Error counting tokens in {file_path}: {str(e)}")
            self.cache[file_path] = 0
            return 0
            
    def get_file_stats(self, file_path: str) -> Tuple[str, float]:
        """Get file token count and percentage of total."""
        tokens = self.count_file_tokens(file_path)
        
        # Format token count
        if tokens >= 1000:
            token_str = f"-{tokens/1000:.1f}k"
        else:
            token_str = f"-{tokens}"
            
        # Calculate percentage
        percentage = (tokens / self.total_tokens * 100) if self.total_tokens > 0 else 0
        
        return token_str, percentage
        
    def get_dir_stats(self, dir_path: str) -> Tuple[str, float]:
        """Get directory total token count and percentage."""
        total_tokens = 0
        
        for root, _, files in os.walk(dir_path):
            # Skip excluded directories
            if any(skip_dir in root.replace('\\', '/').split('/') for skip_dir in self.skip_dirs):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                total_tokens += self.count_file_tokens(file_path)
                
        # Calculate percentage
        percentage = (total_tokens / self.total_tokens * 100) if self.total_tokens > 0 else 0
        
        # Format token count
        if total_tokens >= 1000:
            token_str = f"-{total_tokens/1000:.1f}k"
        else:
            token_str = f"-{total_tokens}"
            
        return token_str, percentage
        
    def update_total_tokens(self, root_path: str):
        """Update the total token count for the project."""
        self.total_tokens = 0
        self.cache.clear()  # Clear cache when updating totals
        
        # First pass: count all tokens
        for root, _, files in os.walk(root_path):
            # Skip excluded directories
            if any(skip_dir in root.replace('\\', '/').split('/') for skip_dir in self.skip_dirs):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                self.total_tokens += self.count_file_tokens(file_path)
                
        logger.debug(f"Updated total tokens: {self.total_tokens}")
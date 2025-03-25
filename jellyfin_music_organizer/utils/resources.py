"""
Resource management for the Jellyfin Music Organizer application.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from .exceptions import FileOperationError
from .constants import APP_NAME

class ResourceManager:
    """
    Manages application resources.
    
    This class:
    1. Handles resource file paths
    2. Manages resource loading
    3. Provides resource validation
    """
    
    def __init__(self, base_path: Optional[str] = None) -> None:
        """
        Initialize the resource manager.
        
        Args:
            base_path: Base path for resources. If None, uses application directory.
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = Path(base_path)
        self.resources: Dict[str, Path] = {}
        
    def register_resource(self, name: str, path: str) -> None:
        """
        Register a resource path.
        
        Args:
            name: Resource name
            path: Path to resource relative to base_path
        """
        full_path = self.base_path / path
        if not full_path.exists():
            raise FileOperationError(f"Resource not found: {path}")
        self.resources[name] = full_path
        
    def get_resource_path(self, name: str) -> Path:
        """
        Get the full path to a resource.
        
        Args:
            name: Resource name
            
        Returns:
            Path to the resource
            
        Raises:
            FileOperationError: If resource is not registered
        """
        if name not in self.resources:
            raise FileOperationError(f"Resource not registered: {name}")
        return self.resources[name]
        
    def get_resource_content(self, name: str) -> bytes:
        """
        Get the content of a resource file.
        
        Args:
            name: Resource name
            
        Returns:
            Resource file content as bytes
            
        Raises:
            FileOperationError: If resource cannot be read
        """
        try:
            return self.get_resource_path(name).read_bytes()
        except Exception as e:
            raise FileOperationError(f"Error reading resource {name}: {e}")
            
    def get_resource_text(self, name: str) -> str:
        """
        Get the content of a text resource file.
        
        Args:
            name: Resource name
            
        Returns:
            Resource file content as string
            
        Raises:
            FileOperationError: If resource cannot be read
        """
        try:
            return self.get_resource_path(name).read_text()
        except Exception as e:
            raise FileOperationError(f"Error reading resource {name}: {e}")
            
    def validate_resources(self) -> bool:
        """
        Validate that all registered resources exist.
        
        Returns:
            True if all resources are valid, False otherwise
        """
        for name, path in self.resources.items():
            if not path.exists():
                return False
        return True 
"""
Security utilities for the Jellyfin Music Organizer application.
"""

import os
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from .exceptions import FileOperationError
from .logger import setup_logger

class SecurityManager:
    """
    Manages application security.
    
    This class:
    1. Handles file permissions
    2. Manages secure storage
    3. Provides input validation
    """
    
    def __init__(self) -> None:
        """Initialize the security manager."""
        self.logger = setup_logger()
        
    def validate_file_permissions(self, path: str, required_permissions: int = 0o644) -> bool:
        """
        Validate file permissions.
        
        Args:
            path: Path to file
            required_permissions: Required permissions in octal format
            
        Returns:
            True if permissions are valid, False otherwise
        """
        try:
            current_permissions = os.stat(path).st_mode & 0o777
            return current_permissions <= required_permissions
        except Exception as e:
            self.logger.error(f"Error checking file permissions: {e}")
            return False
            
    def secure_delete(self, path: str, passes: int = 3) -> None:
        """
        Securely delete a file.
        
        Args:
            path: Path to file
            passes: Number of overwrite passes
            
        Raises:
            FileOperationError: If deletion fails
        """
        try:
            file_size = os.path.getsize(path)
            with open(path, 'wb') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
            os.remove(path)
        except Exception as e:
            raise FileOperationError(f"Error securely deleting file: {e}")
            
    def validate_path(self, path: str) -> bool:
        """
        Validate a file path.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            # Check for path traversal
            if '..' in path or '//' in path:
                return False
                
            # Check for invalid characters
            invalid_chars = '<>:"|?*'
            if any(char in path for char in invalid_chars):
                return False
                
            return True
        except Exception:
            return False
            
    def sanitize_path(self, path: str) -> str:
        """
        Sanitize a file path.
        
        Args:
            path: Path to sanitize
            
        Returns:
            Sanitized path
        """
        # Remove invalid characters
        invalid_chars = '<>:"|?*'
        sanitized = ''.join(char for char in path if char not in invalid_chars)
        
        # Normalize path separators
        sanitized = sanitized.replace('\\', '/')
        
        # Remove path traversal attempts
        parts = sanitized.split('/')
        filtered_parts = []
        for part in parts:
            if part == '..':
                if filtered_parts:
                    filtered_parts.pop()
            elif part and part != '.':
                filtered_parts.append(part)
                
        return '/'.join(filtered_parts)
        
    def calculate_file_hash(self, path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate file hash.
        
        Args:
            path: Path to file
            algorithm: Hash algorithm to use
            
        Returns:
            File hash or None if calculation fails
        """
        try:
            hasher = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return None
            
    def verify_file_integrity(self, path: str, expected_hash: str) -> bool:
        """
        Verify file integrity.
        
        Args:
            path: Path to file
            expected_hash: Expected file hash
            
        Returns:
            True if file integrity is verified, False otherwise
        """
        actual_hash = self.calculate_file_hash(path)
        return actual_hash is not None and actual_hash == expected_hash 
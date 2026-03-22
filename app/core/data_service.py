"""
Data Service - Session-Bound Data Management

This module provides a centralized data service that replaces global state
with session-bound data management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
from flask import request, g
import uuid


@dataclass
class FileMetadata:
    """Metadata for a loaded file."""
    
    display_name: str
    saved_filename: str
    upload_time: datetime
    student_count: int
    class_count: int
    file_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


class DataService:
    """Centralized data service for managing loaded files.
    
    This class replaces the global state in app.py with session-bound data.
    Each session (browser) has its own data context.
    """
    
    def __init__(self):
        """Initialize the data service."""
        # Session storage key (generated per session)
        self._session_id: Optional[str] = None
        self._files: Dict[str, pd.DataFrame] = {}
        self._file_metadata: Dict[str, FileMetadata] = {}
        self._current_file_key: Optional[str] = None
    
    def _get_session_id(self) -> str:
        """Get or create session identifier.
        
        Returns:
            Session identifier string.
        """
        if self._session_id is None:
            self._session_id = str(uuid.uuid4())
        return self._session_id
    
    def load_file(self, display_name: str, df: pd.DataFrame, saved_filename: str) -> None:
        """Load a file into the data service.
        
        Args:
            display_name: Original filename for display.
            df: DataFrame containing the parsed data.
            saved_filename: Actual saved filename on disk.
        """
        # Calculate metadata
        class_count = len(df['class_id'].dropna().unique()) if 'class_id' in df.columns else 0
        
        # Store data
        self._files[display_name] = df
        self._file_metadata[display_name] = FileMetadata(
            display_name=display_name,
            saved_filename=saved_filename,
            upload_time=datetime.now(),
            student_count=len(df),
            class_count=int(class_count)
        )
    
    def get_file_list(self) -> List[str]:
        """Get list of loaded file display names.
        
        Returns:
            List of display names.
        """
        return list(self._files.keys())
    
    def get_file_info(self, display_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file.
        
        Args:
            display_name: Display name of the file.
            
        Returns:
            Dictionary with file metadata or None if not found.
        """
        metadata = self._file_metadata.get(display_name)
        if metadata:
            return {
                'display_name': metadata.display_name,
                'saved_filename': metadata.saved_filename,
                'upload_time': metadata.upload_time.isoformat(),
                'student_count': metadata.student_count,
                'class_count': metadata.class_count,
                'file_id': metadata.file_id
            }
        return None
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Get the currently selected file's data.
        
        Returns:
            DataFrame for current file or None if no file selected.
        """
        if self._current_file_key and self._current_file_key in self._files:
            return self._files[self._current_file_key]
        
        # Fallback to first file if available
        if self._files:
            first_key = list(self._files.keys())[0]
            return self._files[first_key]
        
        return None
    
    def get_current_filename(self) -> Optional[str]:
        """Get the currently selected file's display name.
        
        Returns:
            Display name of current file or None.
        """
        if self._current_file_key and self._current_file_key in self._files:
            return self._current_file_key
        
        # Fallback to first file if available
        if self._files:
            return list(self._files.keys())[0]
        
        return None
    
    def set_current_file(self, display_name: str) -> bool:
        """Set the current file.
        
        Args:
            display_name: Display name of the file to select.
            
        Returns:
            True if file exists and was selected, False otherwise.
        """
        if display_name in self._files:
            self._current_file_key = display_name
            return True
        return False
    
    def get_file_data(self, display_name: str) -> Optional[pd.DataFrame]:
        """Get data for a specific file.
        
        Args:
            display_name: Display name of the file.
            
        Returns:
            DataFrame or None if file not found.
        """
        return self._files.get(display_name)
    
    def remove_file(self, display_name: str) -> bool:
        """Remove a file from the data service.
        
        Args:
            display_name: Display name of the file to remove.
            
        Returns:
            True if file was removed, False if not found.
        """
        if display_name in self._files:
            del self._files[display_name]
            del self._file_metadata[display_name]
            
            # If removed file was current, clear selection
            if self._current_file_key == display_name:
                self._current_file_key = None
            
            return True
        return False
    
    def clear_all(self) -> None:
        """Clear all loaded files."""
        self._files.clear()
        self._file_metadata.clear()
        self._current_file_key = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the data service.
        
        Returns:
            Dictionary with summary statistics.
        """
        total_files = len(self._files)
        total_students = sum(m.student_count for m in self._file_metadata.values())
        total_classes = sum(m.class_count for m in self._file_metadata.values())
        
        return {
            'total_files': total_files,
            'total_students': total_students,
            'total_classes': total_classes,
            'current_file': self._current_file_key,
            'session_id': self._get_session_id()
        }


# Singleton instance for backward compatibility (deprecated)
_data_service_instance: Optional[DataService] = None


def get_data_service() -> DataService:
    """Get the global data service instance (deprecated - use app.data_service).
    
    Returns:
        DataService instance.
    """
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance

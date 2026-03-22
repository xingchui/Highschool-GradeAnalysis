"""
Tests for DataService

This module tests the DataService class functionality.
"""

import pytest
import pandas as pd
from datetime import datetime


class TestDataService:
    """Test cases for DataService."""
    
    def test_load_file(self, data_service):
        """Test loading a file into the data service."""
        file_list = data_service.get_file_list()
        assert 'test_exam.xlsx' in file_list
    
    def test_get_current_data(self, data_service):
        """Test getting current data."""
        current_data = data_service.get_current_data()
        assert current_data is not None
        assert len(current_data) == 5
    
    def test_get_current_filename(self, data_service):
        """Test getting current filename."""
        filename = data_service.get_current_filename()
        assert filename == 'test_exam.xlsx'
    
    def test_set_current_file(self, data_service, sample_dataframe):
        """Test switching current file."""
        # Load another file
        data_service.load_file('another_exam.xlsx', sample_dataframe, 'another_exam.xlsx')
        
        # Switch to it
        result = data_service.set_current_file('another_exam.xlsx')
        assert result is True
        assert data_service.get_current_filename() == 'another_exam.xlsx'
    
    def test_set_nonexistent_file(self, data_service):
        """Test switching to a nonexistent file."""
        result = data_service.set_current_file('nonexistent.xlsx')
        assert result is False
    
    def test_get_file_info(self, data_service):
        """Test getting file metadata."""
        info = data_service.get_file_info('test_exam.xlsx')
        assert info is not None
        assert info['display_name'] == 'test_exam.xlsx'
        assert info['student_count'] == 5
    
    def test_remove_file(self, data_service):
        """Test removing a file."""
        result = data_service.remove_file('test_exam.xlsx')
        assert result is True
        assert 'test_exam.xlsx' not in data_service.get_file_list()
    
    def test_remove_nonexistent_file(self, data_service):
        """Test removing a nonexistent file."""
        result = data_service.remove_file('nonexistent.xlsx')
        assert result is False
    
    def test_clear_all(self, data_service, sample_dataframe):
        """Test clearing all data."""
        # Load another file
        data_service.load_file('another.xlsx', sample_dataframe, 'another.xlsx')
        
        # Clear all
        data_service.clear_all()
        assert len(data_service.get_file_list()) == 0
        assert data_service.get_current_data() is None
    
    def test_get_stats(self, data_service):
        """Test getting statistics."""
        stats = data_service.get_stats()
        assert stats['total_files'] == 1
        assert stats['total_students'] == 5
        assert stats['current_file'] == 'test_exam.xlsx'
    
    def test_fallback_to_first_file(self, data_service):
        """Test fallback behavior when no file is selected."""
        # Clear current selection
        data_service._current_file_key = None
        
        # Should fallback to first file
        current_data = data_service.get_current_data()
        assert current_data is not None
        assert len(current_data) == 5

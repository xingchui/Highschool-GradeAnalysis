"""
Pytest Configuration and Fixtures

This module provides shared fixtures for the test suite.
"""

import pytest
import os
import sys
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def app():
    """Create application for testing.
    
    Yields:
        Flask application configured for testing.
    """
    from app import create_app
    from app.config import TestingConfig
    
    app = create_app(TestingConfig())
    
    yield app


@pytest.fixture
def client(app):
    """Create test client.
    
    Args:
        app: Flask application fixture.
        
    Yields:
        Flask test client.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing.
    
    Returns:
        DataFrame with sample student data.
    """
    data = {
        'student_id': ['001', '002', '003', '004', '005'],
        'name': ['张三', '李四', '王五', '赵六', '钱七'],
        'class_id': ['1', '1', '2', '2', '1'],
        'chinese': [120, 110, 115, 105, 125],
        'math': [130, 125, 120, 115, 135],
        'english': [115, 110, 105, 100, 120],
        'physics': [90, 85, 80, 75, 95],
        'total_scaled': [555, 530, 520, 495, 575],
    }
    return pd.DataFrame(data)


@pytest.fixture
def data_service(app, sample_dataframe):
    """Create a DataService with sample data.
    
    Args:
        app: Flask application fixture.
        sample_dataframe: Sample DataFrame fixture.
        
    Returns:
        DataService instance with sample data loaded.
    """
    # For testing, create a simple data store and DataService
    test_data = {
        'files': {},
        'file_metadata': {},
        'current_file_key': None,
        'created_at': None
    }
    
    from app.core.data_service import DataService, FileMetadata
    from datetime import datetime
    import uuid
    
    # Manually create the data service with test data
    data_service = DataService(test_data)
    data_service.load_file('test_exam.xlsx', sample_dataframe, 'test_exam.xlsx')
    data_service.set_current_file('test_exam.xlsx')
    
    return data_service

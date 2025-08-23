"""
Tests for the main module
"""

import pytest
from src.main import fetch_sample_data, process_data


def test_fetch_sample_data():
    """Test that fetch_sample_data returns data"""
    data = fetch_sample_data()
    assert data is not None
    assert isinstance(data, dict)
    assert "id" in data


def test_process_data():
    """Test that process_data handles data correctly"""
    sample_data = {"id": 1, "title": "Test", "body": "Test body"}
    df = process_data(sample_data)
    assert df is not None
    assert len(df) == 1
    assert df.iloc[0]["id"] == 1


def test_process_data_none():
    """Test that process_data handles None input"""
    df = process_data(None)
    assert df is None

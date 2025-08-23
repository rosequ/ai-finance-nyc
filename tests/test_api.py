"""
Tests for the FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Finance NYC API is running!"}


def test_scrape_endpoint():
    """Test the scrape endpoint with a valid URL"""
    response = client.post(
        "/scrape",
        json={"url": "https://httpbin.org/html"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "title" in data
    assert "content" in data
    assert "status" in data
    assert data["status"] == "success"


def test_scrape_endpoint_invalid_url():
    """Test the scrape endpoint with an invalid URL"""
    response = client.post(
        "/scrape",
        json={"url": "https://invalid-url-that-does-not-exist.com"}
    )
    assert response.status_code == 400
    assert "Failed to fetch URL" in response.json()["detail"]


def test_summarize_endpoint_no_api_key():
    """Test the summarize endpoint without API key (should fail gracefully)"""
    response = client.post(
        "/summarize",
        json={"text": "This is a test text to summarize."}
    )
    # This will fail because no API key is set in test environment
    assert response.status_code in [401, 500]


def test_summarize_endpoint_with_max_length():
    """Test the summarize endpoint with max_length parameter"""
    response = client.post(
        "/summarize",
        json={"text": "This is a test text to summarize.", "max_length": 100}
    )
    # This will fail because no API key is set in test environment
    assert response.status_code in [401, 500]

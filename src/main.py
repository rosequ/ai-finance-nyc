#!/usr/bin/env python3
"""
AI Finance NYC - Main Application
"""

import pandas as pd
import numpy as np
import requests


def fetch_sample_data():
    """Fetch sample financial data"""
    try:
        # Using a free API for demo purposes
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_data(data):
    """Process the fetched data"""
    if data:
        # Create a simple DataFrame
        df = pd.DataFrame([data])
        print("Sample data:")
        print(df)
        return df
    return None


def main():
    """Main application entry point"""
    print("AI Finance NYC - Starting up...")
    
    # Fetch and process data
    data = fetch_sample_data()
    df = process_data(data)
    
    if df is not None:
        print(f"\nData shape: {df.shape}")
        print("Application completed successfully!")
    else:
        print("Failed to process data.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generator function to stream rows from SQL database one by one.
"""

import seed


def stream_users():
    """
    Generator that yields rows one by one from the user_data table.
    
    Yields:
        dict: Dictionary containing user data (user_id, name, email, age)
    """
    # Connect to the database
    connection = seed.connect_to_prodev()
    
    if connection is None:
        return
    
    try:
        # Create cursor with dictionary=True to get results as dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to get all users
        cursor.execute("SELECT * FROM user_data")
        
        # Use generator to yield one row at a time
        for row in cursor:
            yield row
            
    except Exception as e:
        print(f"Error streaming users: {e}")
    
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()
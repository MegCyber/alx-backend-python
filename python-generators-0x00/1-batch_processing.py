#!/usr/bin/env python3
"""
Batch processing functions to fetch and process data in batches from users database.
"""

import seed


def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows in batches from the user_data table.
    
    Args:
        batch_size (int): Number of rows to fetch in each batch
        
    Yields:
        list: List of dictionaries containing user data
    """
    connection = seed.connect_to_prodev()
    
    if connection is None:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        while True:
            # Fetch batch with LIMIT and OFFSET
            query = f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}"
            cursor.execute(query)
            batch = cursor.fetchall()
            
            # If no more rows, break
            if not batch:
                break
                
            yield batch
            offset += batch_size
            
    except Exception as e:
        print(f"Error streaming users in batches: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size (int): Size of each batch to process
    """
    # Process each batch from the generator
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25
        for user in batch:
            if user['age'] > 25:
                print(user)
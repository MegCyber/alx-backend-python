#!/usr/bin/env python3
"""
Lazy pagination implementation using generators to fetch paginated data on demand.
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetches users with pagination using LIMIT and OFFSET.
    
    Args:
        page_size (int): Number of users per page
        offset (int): Starting offset for the query
        
    Returns:
        list: List of user dictionaries for the requested page
    """
    connection = seed.connect_to_prodev()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        return rows
    
    except Exception as e:
        print(f"Error paginating users: {e}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def lazy_paginate(page_size):
    """
    Generator function that lazily loads pages of users only when needed.
    
    Args:
        page_size (int): Number of users per page
        
    Yields:
        list: Page of user dictionaries
    """
    offset = 0
    
    while True:
        # Fetch the next page
        page = paginate_users(page_size, offset)
        
        # If no more data, stop iteration
        if not page:
            break
            
        yield page
        offset += page_size


# Alias for the function name expected in the test
lazy_pagination = lazy_paginate
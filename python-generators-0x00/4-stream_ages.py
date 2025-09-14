#!/usr/bin/env python3
"""
Memory-efficient aggregation using generators to compute average age from large dataset.
"""

import seed


def stream_user_ages():
    """
    Generator that yields user ages one by one from the user_data table.
    
    Yields:
        int: User age
    """
    connection = seed.connect_to_prodev()
    
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        
        # Query to get only age column for memory efficiency
        cursor.execute("SELECT age FROM user_data")
        
        # Yield ages one by one
        for (age,) in cursor:
            yield age
            
    except Exception as e:
        print(f"Error streaming user ages: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculate average age using generator without loading entire dataset into memory.
    
    Returns:
        float: Average age of all users
    """
    total_age = 0
    count = 0
    
    # Use generator to process ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0
    
    return total_age / count


if __name__ == "__main__":
    """
    Main execution to calculate and display average age.
    """
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")
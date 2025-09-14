#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries
"""

import asyncio
import aiosqlite
import sqlite3
import time


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All users from the users table
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT * FROM users")
            results = await cursor.fetchall()
            print("async_fetch_users: Fetched all users")
            return results
    except Exception as e:
        print(f"Error in async_fetch_users: {e}")
        return []


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: Users older than 40 from the users table
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
            results = await cursor.fetchall()
            print("async_fetch_older_users: Fetched users older than 40")
            return results
    except Exception as e:
        print(f"Error in async_fetch_older_users: {e}")
        return []


async def fetch_concurrently():
    """
    Execute both async_fetch_users and async_fetch_older_users concurrently
    using asyncio.gather().
    
    Returns:
        tuple: Results from both queries (all_users, older_users)
    """
    print("Starting concurrent database queries...")
    start_time = time.time()
    
    # Execute both queries concurrently using asyncio.gather()
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    end_time = time.time()
    print(f"Concurrent queries completed in {end_time - start_time:.4f} seconds")
    
    return all_users, older_users


def setup_database():
    """
    Set up the database with sample data for testing.
    """
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            sample_users = [
                ('Alice', 30),
                ('Bob', 25),
                ('Charlie', 35),
                ('Diana', 28),
                ('Eve', 42),
                ('Frank', 19),
                ('Grace', 55),
                ('Henry', 33),
                ('Ivy', 41),
                ('Jack', 29),
                ('Kate', 47),
                ('Liam', 38)
            ]
            cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            conn.commit()
            print("Sample data inserted into users table")


def display_results(all_users, older_users):
    """
    Display the results from both queries in a formatted manner.
    
    Args:
        all_users (list): Results from fetching all users
        older_users (list): Results from fetching users older than 40
    """
    print("\n" + "="*50)
    print("CONCURRENT QUERY RESULTS")
    print("="*50)
    
    print(f"\n--- All Users ({len(all_users)} records) ---")
    print("ID | Name     | Age")
    print("-" * 25)
    for user in all_users:
        print(f"{user[0]:<2} | {user[1]:<8} | {user[2]}")
    
    print(f"\n--- Users Older Than 40 ({len(older_users)} records) ---")
    print("ID | Name     | Age")
    print("-" * 25)
    for user in older_users:
        print(f"{user[0]:<2} | {user[1]:<8} | {user[2]}")


async def demo_sequential_vs_concurrent():
    """
    Demonstrate the performance difference between sequential and concurrent execution.
    """
    print("\n" + "="*50)
    print("PERFORMANCE COMPARISON")
    print("="*50)
    
    # Sequential execution
    print("\n--- Sequential Execution ---")
    start_time = time.time()
    all_users_seq = await async_fetch_users()
    older_users_seq = await async_fetch_older_users()
    sequential_time = time.time() - start_time
    print(f"Sequential execution time: {sequential_time:.4f} seconds")
    
    # Concurrent execution
    print("\n--- Concurrent Execution ---")
    start_time = time.time()
    all_users_conc, older_users_conc = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    concurrent_time = time.time() - start_time
    print(f"Concurrent execution time: {concurrent_time:.4f} seconds")
    
    # Calculate improvement
    if sequential_time > 0:
        improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
        print(f"Performance improvement: {improvement:.2f}%")


def main():
    """
    Main function to demonstrate concurrent asynchronous database queries.
    """
    # Set up the database
    setup_database()
    
    print("\n--- Concurrent Asynchronous Database Queries ---")
    
    # Run the concurrent fetch operation
    all_users, older_users = asyncio.run(fetch_concurrently())
    
    # Display the results
    display_results(all_users, older_users)
    
    # Optional: Demonstrate performance comparison
    print("\n--- Running Performance Comparison ---")
    asyncio.run(demo_sequential_vs_concurrent())


if __name__ == "__main__":
    main()
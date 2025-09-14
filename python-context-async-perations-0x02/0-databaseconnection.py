#!/usr/bin/env python3
"""
Custom class-based context manager for Database connection
"""

import sqlite3


class DatabaseConnection:
    """
    A custom context manager class for handling database connections.
    
    This class implements the context manager protocol using __enter__ and __exit__
    methods to automatically handle database connection opening and closing.
    """
    
    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection with a database name.
        
        Args:
            db_name (str): The name/path of the database file
        """
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context - open the database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        self.connection = sqlite3.connect(self.db_name)
        print(f"Database connection to '{self.db_name}' opened")
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context - close the database connection.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)  
            exc_tb: Exception traceback (if any)
        """
        if self.connection:
            self.connection.close()
            print(f"Database connection to '{self.db_name}' closed")
        
        # Return False to propagate any exceptions
        return False


def main():
    """
    Demonstrate the usage of DatabaseConnection context manager.
    """
    # First, let's create a sample database with users table for testing
    db_name = "users.db"
    
    # Create and populate the database
    with sqlite3.connect(db_name) as conn:
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
                ('Eve', 42)
            ]
            cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            conn.commit()
            print("Sample data inserted into users table")
    
    # Now demonstrate the custom context manager
    print("\n--- Using Custom DatabaseConnection Context Manager ---")
    
    with DatabaseConnection(db_name) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("\nQuery Results from 'SELECT * FROM users':")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:<2} | {row[1]:<7} | {row[2]}")


if __name__ == "__main__":
    main()
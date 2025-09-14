#!/usr/bin/env python3
"""
Reusable Query Context Manager
"""

import sqlite3


class ExecuteQuery:
    """
    A reusable context manager class that handles both database connection
    and query execution with parameters.
    
    This class takes a query and parameters, manages the database connection,
    executes the query, and returns the results.
    """
    
    def __init__(self, db_name, query, params=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name (str): The name/path of the database file
            query (str): The SQL query to execute
            params (tuple): Parameters for the SQL query (optional)
        """
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context - open connection, execute query, and return results.
        
        Returns:
            list: The query results
        """
        try:
            # Open database connection
            self.connection = sqlite3.connect(self.db_name)
            print(f"Database connection to '{self.db_name}' opened")
            
            # Execute the query
            cursor = self.connection.cursor()
            cursor.execute(self.query, self.params)
            self.results = cursor.fetchall()
            
            print(f"Query executed: {self.query}")
            if self.params:
                print(f"Parameters: {self.params}")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            if self.connection:
                self.connection.close()
            raise
    
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


def setup_database(db_name):
    """
    Set up the database with sample data for testing.
    
    Args:
        db_name (str): The name/path of the database file
    """
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
                ('Eve', 42),
                ('Frank', 19),
                ('Grace', 55),
                ('Henry', 33)
            ]
            cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", sample_users)
            conn.commit()
            print("Sample data inserted into users table")


def main():
    """
    Demonstrate the usage of ExecuteQuery context manager.
    """
    db_name = "users.db"
    
    # Set up the database
    setup_database(db_name)
    
    print("\n--- Using ExecuteQuery Context Manager ---")
    
    # Use the ExecuteQuery context manager to fetch users older than 25
    query = "SELECT * FROM users WHERE age > ?"
    age_threshold = 25
    
    with ExecuteQuery(db_name, query, (age_threshold,)) as results:
        print(f"\nResults for users older than {age_threshold}:")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:<2} | {row[1]:<7} | {row[2]}")
    
    print("\n--- Additional Query Example ---")
    
    # Another example with a different query
    query2 = "SELECT name, age FROM users WHERE age BETWEEN ? AND ?"
    min_age, max_age = 25, 40
    
    with ExecuteQuery(db_name, query2, (min_age, max_age)) as results:
        print(f"\nUsers between ages {min_age} and {max_age}:")
        print("Name    | Age")
        print("-" * 12)
        for row in results:
            print(f"{row[0]:<7} | {row[1]}")


if __name__ == "__main__":
    main()
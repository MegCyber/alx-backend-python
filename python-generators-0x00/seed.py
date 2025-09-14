#!/usr/bin/env python3
"""
Database setup module for ALX_prodev database with user_data table.
"""

import mysql.connector
import csv
import uuid
from mysql.connector import Error


def connect_db():
    """
    Connects to the MySQL database server.
    
    Returns:
        connection object if successful, None otherwise
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'  # Update with your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection object if successful, None otherwise
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',  # Update with your MySQL password
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data into the database if it does not exist.
    
    Args:
        connection: MySQL connection object
        csv_file: path to the CSV file containing user data
    """
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("Data already exists in the table")
            cursor.close()
            return
        
        # Read CSV file and insert data
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            
            for row in csv_reader:
                # Generate UUID for user_id if not present
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = int(row['age'])
                
                cursor.execute(insert_query, (user_id, name, email, age))
        
        connection.commit()
        cursor.close()
        print("Data inserted successfully")
        
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
    except Exception as e:
        print(f"Unexpected error: {e}")
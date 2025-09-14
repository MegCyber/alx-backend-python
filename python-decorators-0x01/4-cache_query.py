import time
import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that automatically handles database connection opening and closing"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    return wrapper

query_cache = {}

def cache_query(func):
    """Decorator that caches query results based on the SQL query string"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from arguments
        query = None
        if args and len(args) > 1:
            # Check if query is in positional args (after conn)
            query = args[1] if isinstance(args[1], str) else kwargs.get('query')
        elif 'query' in kwargs:
            query = kwargs['query']
        
        if query:
            # Check if result is cached
            if query in query_cache:
                print(f"Cache hit for query: {query}")
                return query_cache[query]
            
            # Execute function and cache result
            print(f"Cache miss. Executing query: {query}")
            result = func(*args, **kwargs)
            query_cache[query] = result
            return result
        else:
            # If no query found, execute without caching
            return func(*args, **kwargs)
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
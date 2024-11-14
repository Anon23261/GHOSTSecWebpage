import redis

try:
    # Try to connect to Memurai
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Test the connection
    r.ping()
    print("Successfully connected to Memurai!")
    
    # Try to set and get a value
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"Test value retrieved: {value}")
    
except redis.ConnectionError as e:
    print(f"Failed to connect to Memurai: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

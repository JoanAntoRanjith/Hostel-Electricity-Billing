from db import get_connection

connection = get_connection()

print("✅ Successfully connected to Supabase PostgreSQL!")

connection.close()

print("✅ Connection closed.")
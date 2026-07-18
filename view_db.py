import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('users.db')

# Read all users
df = pd.read_sql_query("SELECT * FROM users", conn)

print("All users in database:")
print(df)

conn.close()
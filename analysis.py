import sqlite3
import pandas as pd

# Example query to get all matches
conn = sqlite3.connect('ipl_commentary.db')
matches_df = pd.read_sql("SELECT * FROM matches", conn)
commentary_df = pd.read_sql("SELECT * FROM commentary", conn)
print(matches_df.head())
print(commentary_df.head())

print("Mathces Shape: ", matches_df.shape)
print("Commentary Shape: ", commentary_df.shape)


conn.close()
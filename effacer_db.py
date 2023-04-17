import sqlite3

# Connect to the database
conn = sqlite3.connect('db/db')
c = conn.cursor()

# Clear all the data in the table
c.execute('DELETE FROM poursuite')
c.execute('DELETE FROM utilisateurs')
c.execute('DELETE FROM plaintes')

# Commit the changes and close the database connection
conn.commit()
conn.close()

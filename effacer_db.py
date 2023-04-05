import sqlite3

# Connect to the database
conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
c = conn.cursor()

# Clear all the data in the table
c.execute('DELETE FROM poursuite')

# Commit the changes and close the database connection
conn.commit()
conn.close()

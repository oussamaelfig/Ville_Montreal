import psycopg2

# Connect to the database
conn = psycopg2.connect('db/db')
c = conn.cursor()

# Clear all the data in the table
c.execute('DELETE FROM poursuite')

# Commit the changes and close the database connection
conn.commit()
conn.close()

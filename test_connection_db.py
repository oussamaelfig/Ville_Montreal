import psycopg2


def test_connection():
    try:
        conn = psycopg2.connect(
            dbname="db",
            user="postgres",
            password="Admin@2023",
            host="localhost",
            port="5432"
        )
        print("Connection to PostgreSQL database successful!")
        c = conn.cursor()
        c.execute("SELECT * FROM poursuite")

        # Fetch the results
        rows = c.fetchall()

        # Print the results
        for row in rows:
            print(row)

        # Close the cursor and connection
        c.close()
        conn.close()

    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)


print("Testing connection...")
test_connection()
print("Done.")

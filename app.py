from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# Define the routes for the application
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():
    # Extract the search query from the form
    query = request.form.get("query")

    # Connect to the database
    conn = sqlite3.connect("db/db")
    c = conn.cursor()

    # Query the database
    c.execute("SELECT * FROM poursuite WHERE etablissement LIKE ? OR "
              "proprietaire LIKE ? OR adresse LIKE ?", ('%' + query + '%',
                                                        '%' + query + '%',
                                                        '%' + query + '%'))
    result = c.fetchall()

    # Close the connection to the database
    conn.close()

    return render_template("search.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)

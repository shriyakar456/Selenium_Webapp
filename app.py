from flask import Flask, render_template, request, redirect, url_for, session
import json
import psycopg2
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.secret_key = 'supersecretkey'  # Make sure to use a secure key in production

# --- Load Users from JSON ---
with open('users.json', 'r') as f:
    USERS = json.load(f)

# --- PostgreSQL Connection ---
def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            port=5434,  
            database="webapp_db",
            user="postgres",
            password="ruchi123"
        )
    except Exception as e:
        print("Database connection failed:", e)
        raise

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        # Validate login against JSON users
        if any(user["username"] == uname and user["password"] == pwd for user in USERS):
            session['username'] = uname
            return redirect(url_for('form'))
        else:
            error = "Invalid username or password!"
    return render_template('login.html', error=error)

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Capture form data
        name = request.form['name']
        email = request.form['email']
        rating = request.form['rating']
        category = request.form['category']
        product = request.form['product']
        comments = request.form['comments']

        # Insert data into PostgreSQL database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO feedback (username, name, email, rating, category, product, comments) VALUES (%s, %s, %s, %s, %s, %s, %s) ", (session['username'], name, email, rating, category, product, comments))
        conn.commit()
        cur.close()
        conn.close()

        return f"<h2>Thank you, {name}! Your feedback has been submitted.</h2>"

    return render_template('form.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)

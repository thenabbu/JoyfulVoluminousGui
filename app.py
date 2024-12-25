from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "navya",
    "database": "sentidb"
}

# Initialize database and create tables
def init_db():
    try:
        # Connect without specifying the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="navya"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS sentidb")
        cursor.close()
        conn.close()

        # Now connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Create tables...
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid VARCHAR(10) PRIMARY KEY,
                fname VARCHAR(255),
                lname VARCHAR(255),
                email VARCHAR(255),
                pwd VARCHAR(255),
                gender VARCHAR(10),
                height FLOAT,
                weight FLOAT,
                dob DATE,
                state VARCHAR(255),
                city VARCHAR(255)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                cid VARCHAR(10) PRIMARY KEY,
                company VARCHAR(255),
                email VARCHAR(255),
                pwd VARCHAR(255)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                pid VARCHAR(10) PRIMARY KEY,
                cid VARCHAR(10),
                product VARCHAR(255),
                thumbnail TEXT,
                barcode TEXT,
                FOREIGN KEY (cid) REFERENCES companies(cid)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                fid VARCHAR(10) PRIMARY KEY,
                uid VARCHAR(10),
                pid VARCHAR(10),
                feedback TEXT,
                sentiment VARCHAR(20),
                FOREIGN KEY (uid) REFERENCES users(uid),
                FOREIGN KEY (pid) REFERENCES products(pid)
            );
        """)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

init_db()

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        uid = request.form['uid']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        gender = request.form['gender']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        dob = request.form['dob']
        state = request.form['state']
        city = request.form['city']

        # Insert data into the users table
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO users (uid, fname, lname, email, pwd, gender, height, weight, dob, state, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (uid, fname, lname, email, pwd, gender, height, weight, dob, state, city)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to login page
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        # Query the database for the user
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE email = %s AND pwd = %s"
        values = (email, pwd)
        cursor.execute(query, values)
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            # Store user id in session
            session['uid'] = user[0]
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            return "Invalid email or password"
    return render_template('user_login.html')

@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        cid = request.form['cid']
        company = request.form['company']
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])

        # Insert data into the companies table
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO companies (cid, company, email, pwd)
            VALUES (%s, %s, %s, %s)
        """
        values = (cid, company, email, pwd)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to login page
        return redirect(url_for('company_login'))
    return render_template('company_register.html')

@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        # Query the database for the company
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM companies WHERE email = %s AND pwd = %s"
        values = (email, pwd)
        cursor.execute(query, values)
        company = cursor.fetchone()
        cursor.close()
        conn.close()
        if company:
            # Store company id in session
            session['cid'] = company[0]
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            return "Invalid email or password"
    return render_template('company_login.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'uid' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        fid = request.form['fid']
        uid = session['uid']
        pid = request.form['pid']
        feedback_text = request.form['feedback']
        sentiment = request.form['sentiment']

        # Insert data into the feedback table
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO feedback (fid, uid, pid, feedback, sentiment)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (fid, uid, pid, feedback_text, sentiment)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to index page
        return redirect(url_for('index'))
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True)

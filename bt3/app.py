from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Connection details and global variable for the database connection
db_connection_params = {}
conn = None

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the database connection form
@app.route('/login')
def login():
    return render_template('login.html')

# Route for connecting to the database
@app.route('/connect_db', methods=['POST'])
def connect_db():
    global db_connection_params, conn
    # Retrieve form data
    db_connection_params = {
        'dbname': request.form['db_name'],
        'user': request.form['user'],
        'password': request.form['password'],
        'host': request.form['host'],
        'port': request.form['port'],
        'table_name': request.form['table_name']
    }

    try:
        # Attempt to connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=db_connection_params['dbname'],
            user=db_connection_params['user'],
            password=db_connection_params['password'],
            host=db_connection_params['host'],
            port=db_connection_params['port']
        )
        flash("Successfully connected to the database!", "success")
        return redirect(url_for('student_management'))
    except Exception as e:
        flash(f"Failed to connect to the database: {e}", "error")
        return redirect(url_for('login'))

# Route for student management (CRUD operations)
@app.route('/student_management')
def student_management():
    global conn, db_connection_params
    if conn is None:
        flash("Not connected to a database.", "error")
        return redirect(url_for('login'))

    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(db_connection_params['table_name'])))
        students = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f"Failed to load students: {e}", "error")
        students = []

    return render_template('student_management.html', students=students)

# Route to add a student
@app.route('/add_student', methods=['POST'])
def add_student():
    global conn, db_connection_params
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    major = request.form['major']

    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("INSERT INTO {} (name, age, gender, major) VALUES (%s, %s, %s, %s)").format(sql.Identifier(db_connection_params['table_name'])),
                    (name, age, gender, major))
        conn.commit()
        cur.close()
        flash("Student added successfully!", "success")
    except Exception as e:
        flash(f"Failed to add student: {e}", "error")

    return redirect(url_for('student_management'))

# Route to update a student (simple form and handler)
@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    global conn, db_connection_params
    if request.method == 'POST':
        # Process the form data and update the student in the database
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        major = request.form['major']

        try:
            cur = conn.cursor()
            cur.execute(sql.SQL("UPDATE {} SET name = %s, age = %s, gender = %s, major = %s WHERE id = %s").format(sql.Identifier(db_connection_params['table_name'])),
                        (name, age, gender, major, student_id))
            conn.commit()
            cur.close()
            flash("Student updated successfully!", "success")
        except Exception as e:
            flash(f"Failed to update student: {e}", "error")

        return redirect(url_for('student_management'))

    else:
        # Fetch the current data of the student for display in the form
        try:
            cur = conn.cursor()
            cur.execute(sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(db_connection_params['table_name'])), (student_id,))
            student = cur.fetchone()
            cur.close()
        except Exception as e:
            flash(f"Failed to load student data: {e}", "error")
            return redirect(url_for('student_management'))

        # Render the update form with the current student data
        return render_template('update_student.html', student=student)

# Route to delete a student
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    global conn, db_connection_params
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(db_connection_params['table_name'])),
                    (student_id,))
        conn.commit()
        cur.close()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete student: {e}", "error")

    return redirect(url_for('student_management'))

if __name__ == "__main__":
    app.run(debug=True)
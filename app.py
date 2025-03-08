import os
import mysql.connector  # Replaced psycopg2 with mysql.connector
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from pathlib import Path

# Define SheetDB API URL
SHEETDB_REGISTRATION_URL = "https://sheetdb.io/api/v1/lvg1wuw9n1k20"

# Create the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["https://face-attendance-github-io.onrender.com"])

# MySQL Configuration for qr_code_attendance (Student Registration)
MYSQL_HOST_REG = os.getenv("MYSQL_HOST_REG", "localhost")
MYSQL_USER_REG = os.getenv("MYSQL_USER_REG", "root")
MYSQL_PASSWORD_REG = os.getenv("MYSQL_PASSWORD_REG", "master@123")
MYSQL_DATABASE_REG = os.getenv("MYSQL_DATABASE_REG", "face_attendance")
MYSQL_PORT_REG = os.getenv("MYSQL_PORT_REG", "3306")

# MySQL Configuration for qr_code_attendance_making (Attendance)
MYSQL_HOST_ATT = os.getenv("MYSQL_HOST_ATT", "localhost")
MYSQL_USER_ATT = os.getenv("MYSQL_USER_ATT", "root")
MYSQL_PASSWORD_ATT = os.getenv("MYSQL_PASSWORD_ATT", "master@123")
MYSQL_DATABASE_ATT = os.getenv("MYSQL_DATABASE_ATT", "face_attendance")
MYSQL_PORT_ATT = os.getenv("MYSQL_PORT_ATT", "3306")

# Upload Folder Configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Initialize MySQL Database Connection for Student Registration
def get_db_connection_reg():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST_REG,
            user=MYSQL_USER_REG,
            password=MYSQL_PASSWORD_REG,
            database=MYSQL_DATABASE_REG,
            port=MYSQL_PORT_REG
        )
        print("✅ Connected to MySQL (Registration)!")
        return conn
    except mysql.connector.Error as err:
        print("⚠️ MySQL Error (Registration):", err)
        return None

# Initialize MySQL Database Connection for Attendance
def get_db_connection_att():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST_ATT,
            user=MYSQL_USER_ATT,
            password=MYSQL_PASSWORD_ATT,
            database=MYSQL_DATABASE_ATT,
            port=MYSQL_PORT_ATT
        )
        print("✅ Connected to MySQL (Attendance)!")
        return conn
    except mysql.connector.Error as err:
        print("⚠️ MySQL Error (Attendance):", err)
        return None

# Create User-Specific Student Registration Table
def create_user_student_table(username):
    conn = get_db_connection_reg()
    if not conn:
        return False

    cursor = conn.cursor()
    table_name = f"students_{username}"
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rollNumber VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            father_name VARCHAR(255) NOT NULL,
            mother_name VARCHAR(255) NOT NULL,
            date_of_birth DATE NOT NULL,
            class VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            gender VARCHAR(255) NOT NULL,
            academicYear VARCHAR(255) NOT NULL,
            faceDescriptor JSON NOT NULL  -- Store face descriptor as JSON
        )
    ''')
    conn.commit()
    conn.close()
    return True

# Initialize MySQL Databases
def init_db():
    # Initialize Registration Database
    conn_reg = get_db_connection_reg()
    if conn_reg:
        conn_reg.close()
        print("✅ Registration Database initialized!")
    else:
        print("⚠️ Failed to initialize Registration Database.")

    # Initialize Attendance Database
    conn_att = get_db_connection_att()
    if conn_att:
        cursor_att = conn_att.cursor()
        # Create a general attendance table (optional, can be removed if not needed)
        cursor_att.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                rollNumber VARCHAR(255) NOT NULL,
                time VARCHAR(255) NOT NULL,
                date VARCHAR(255) NOT NULL
            )
        ''')
        conn_att.commit()
        conn_att.close()
        print("✅ Attendance Database initialized!")
    else:
        print("⚠️ Failed to initialize Attendance Database.")

init_db()  # Run database setup

# Serve static files (frontend)
# Serve static files (frontend)
# Serve static files (frontend)
# Serve static files (frontend)
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/attendance_summary')
def serve_attendance_summary():
    return send_from_directory('static', 'attendance_summary.html')

# Serve static files from the 'static' folder
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Serve model files from the 'weights' folder
@app.route('/weights/<path:filename>')
def serve_weights(filename):
    return send_from_directory('weights', filename)

# Register Student API
# Register Student API
@app.route('/register_student', methods=['POST'])
def register_student():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract data from the request
    username = data.get("username")
    rollNumber = data.get("rollNumber")
    name = data.get("name")
    father_name = data.get("father_name")
    mother_name = data.get("mother_name")
    date_of_birth = data.get("date_of_birth")
    category = data.get("category")
    gender = data.get("gender")
    classValue = data.get("class")
    academicYear = data.get("academicYear")
    faceDescriptor = data.get("faceDescriptor")  # Extract face descriptor

    try:
        # Connect to the database
        conn = get_db_connection_reg()
        if not conn:
            return jsonify({"error": "Database connection error"}), 500

        cursor = conn.cursor()
        table_name = f"students_{username}"

        # Insert the student data into the database
        cursor.execute(
            f"INSERT INTO {table_name} (rollNumber, name, father_name, mother_name, date_of_birth, class, category, gender, academicYear, faceDescriptor) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (rollNumber, name, father_name, mother_name, date_of_birth, classValue, category, gender, academicYear, json.dumps(faceDescriptor))  # Store face descriptor as JSON
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Student registration successful"})

    except mysql.connector.Error as e:
        print("⚠️ MySQL Error:", str(e))
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print("⚠️ Server error:", str(e))
        return jsonify({"error": "Server error: Could not register student"}), 500

# Fetch Student Details API
# Fetch Student Details API
@app.route('/student_details/<username>/<rollNumber>', methods=['GET', 'OPTIONS'])
def student_details(username, rollNumber):
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET")
        return response, 200

    conn = get_db_connection_reg()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    cursor = conn.cursor()
    table_name = f"students_{username}"
    cursor.execute(
        f"SELECT * FROM {table_name} WHERE rollNumber = %s",
        (rollNumber,)
    )
    student = cursor.fetchone()
    conn.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Map database fields to response
    student_data = {
        "rollNumber": student[1],
        "name": student[2],
        "father_name": student[3],
        "mother_name": student[4],
        "date_of_birth": student[5].strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
        "class": student[6],
        "category": student[7],
        "gender": student[8],
        "academicYear": student[9],
        "faceDescriptor": json.loads(student[10])  # Parse JSON string to object
    }

    return jsonify({"student": student_data})

# Create User-Specific Attendance Table
def create_user_attendance_table(username):
    conn = get_db_connection_att()
    if not conn:
        return False

    cursor = conn.cursor()
    table_name = f"attendance_{username}"
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rollNumber VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            father_name VARCHAR(255) NOT NULL,
            mother_name VARCHAR(255) NOT NULL,
            date_of_birth DATE NOT NULL,
            class VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            gender VARCHAR(255) NOT NULL,
            academicYear VARCHAR(255) NOT NULL,
            attendance_month VARCHAR(255) NOT NULL,
            time VARCHAR(255) NOT NULL,
            date VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return True

# Mark Attendance API
@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    print("Incoming Attendance Data:", data)  # Debugging

    username = data.get("username")
    rollNumber = data.get("rollNumber")
    name = data.get("name")
    father_name = data.get("father_name")
    mother_name = data.get("mother_name")
    date_of_birth = data.get("date_of_birth")
    classValue = data.get("class")
    category = data.get("category")
    gender = data.get("gender")
    academicYear = data.get("academicYear")
    attendance_month = data.get("attendance_month")
    time = data.get("time")
    date = data.get("date")

    try:
        if not create_user_attendance_table(username):
            return jsonify({"error": "Database connection error"}), 500

        conn = get_db_connection_att()
        if not conn:
            return jsonify({"error": "Database connection error"}), 500

        cursor = conn.cursor()
        table_name = f"attendance_{username}"

        # Check if attendance for the same date already exists
        cursor.execute(
            f"SELECT * FROM {table_name} WHERE rollNumber = %s AND date = %s",
            (rollNumber, date)
        )
        existing_attendance = cursor.fetchone()

        if existing_attendance:
            conn.close()
            return jsonify({"error": "Attendance already marked for this date"}), 400

        # Insert the attendance data into the user-specific table
        cursor.execute(
            f"INSERT INTO {table_name} (rollNumber, name, father_name, mother_name, date_of_birth, class, category, gender, academicYear, attendance_month, time, date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (rollNumber, name, father_name, mother_name, date_of_birth, classValue, category, gender, academicYear, attendance_month, time, date)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Attendance marked successfully"})

    except mysql.connector.Error as e:
        print("⚠️ MySQL Error:", str(e))
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print("⚠️ Server error:", str(e))
        return jsonify({"error": "Server error: Could not mark attendance"}), 500

@app.route('/attendance_summary/<username>', methods=['GET'])
def get_attendance_summary(username):
    month = request.args.get('month')
    if not month:
        return jsonify({"error": "Month parameter is required"}), 400

    # Convert numeric month to month name
    month_names = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    month_name = month_names.get(month)
    if not month_name:
        return jsonify({"error": "Invalid month value"}), 400

    try:
        conn = get_db_connection_att()
        if not conn:
            return jsonify({"error": "Database connection error"}), 500

        cursor = conn.cursor()
        table_name = f"attendance_{username}"

        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Attendance table not found"}), 404

        # Fetch all unique working days in the selected month
        cursor.execute(
            f"SELECT DISTINCT date FROM {table_name} WHERE attendance_month = %s",
            (month_name,)
        )
        working_days = cursor.fetchall()
        total_working_days = len(working_days)

        # Fetch all students from the registration table, sorted by rollNumber numerically
        conn_reg = get_db_connection_reg()
        if not conn_reg:
            return jsonify({"error": "Database connection error"}), 500

        cursor_reg = conn_reg.cursor()
        student_table_name = f"students_{username}"
        cursor_reg.execute(f"SELECT * FROM {student_table_name} ORDER BY CAST(rollNumber AS UNSIGNED)")
        students = cursor_reg.fetchall()
        conn_reg.close()

        attendance_summary = []
        for student in students:
            rollNumber = student[1]
            name = student[2]
            father_name = student[3]
            date_of_birth = student[5].strftime('%d-%m-%y')
            classValue = student[6]
            category = student[7]
            gender = student[8]
            academicYear = student[9]

            # Fetch attendance records for the selected month and count distinct dates
            cursor.execute(
                f"SELECT COUNT(DISTINCT date) FROM {table_name} WHERE rollNumber = %s AND attendance_month = %s",
                (rollNumber, month_name)
            )
            days_present = cursor.fetchone()[0]  # Get the count of distinct dates

            # Calculate days absent
            days_absent = total_working_days - days_present

            attendance_summary.append({
                "rollNumber": rollNumber,
                "name": name,
                "father_name": father_name,
                "date_of_birth": date_of_birth,
                "class": classValue,
                "category": category,
                "gender": gender,
                "academicYear": academicYear,
                "days_present": days_present,
                "days_absent": days_absent
            })

        conn.close()
        return jsonify({
            "attendance_summary": attendance_summary,
            "total_working_days": total_working_days
        })

    except mysql.connector.Error as e:
        print("⚠️ MySQL Error:", str(e))
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print("⚠️ Server error:", str(e))
        return jsonify({"error": "Server error: Could not fetch attendance summary"}), 500

# Fetch Attendance Records API
# Fetch Attendance Records API
@app.route('/attendance_records/<username>', methods=['GET'])
def get_attendance_records(username):
    try:
        conn = get_db_connection_att()
        if not conn:
            return jsonify({"error": "Database connection error"}), 500

        cursor = conn.cursor()
        table_name = f"attendance_{username}"

        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Attendance table not found"}), 404

        # Fetch records from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        records = cursor.fetchall()
        conn.close()

        attendance_records = []
        for record in records:
            attendance_records.append({
                "rollNumber": record[1],
                "name": record[2],
                "father_name": record[3],
                "mother_name": record[4],
                "date_of_birth": record[5].strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
                "class": record[6],
                "category": record[7],
                "gender": record[8],
                "academicYear": record[9],
                "attendance_month": record[10],
                "time": record[11],
                "date": record[12]
            })

        return jsonify({"records": attendance_records})

    except mysql.connector.Error as e:  # Replaced psycopg2.Error with mysql.connector.Error
        print("⚠️ MySQL Error:", str(e))
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print("⚠️ Server error:", str(e))
        return jsonify({"error": "Server error: Could not fetch attendance records"}), 500

# Start the Flask Server
if __name__ == '__main__':
    print(f"🚀 Starting server on port 5500...")
    app.run(host="0.0.0.0", port=5500, debug=False)
    
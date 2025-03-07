from flask import Flask, send_from_directory

app = Flask(__name__)

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

if __name__ == '__main__':
    print(f"🚀 Starting server on port 5500...")
    app.run(host="0.0.0.0", port=5500, debug=False)
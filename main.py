from config import app

from routes import home, register, log_in, log_out, schedule_goals, process_data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
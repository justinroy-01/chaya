from flask import Flask, render_template, jsonify
import serial
import threading
import time
import os 

# --- Global Variables ---
app_data = {
    "temperature": "N/A" 
}
data_lock = threading.Lock()
is_reading = True # NEW: Flag to control the reading loop

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Background Thread for Reading Arduino Data ---
def read_from_arduino():
    """
    This function now checks the 'is_reading' flag before updating the temperature.
    """
    global app_data, is_reading
    
    while True:
        try:
            arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
            print("Arduino connected!")
            break
        except serial.SerialException:
            print("Arduino not found on COM3. Retrying in 5 seconds...")
            time.sleep(5)

    while True:
        # The loop will only read and update data if is_reading is True
        if is_reading and arduino.in_waiting > 0:
            try:
                raw_data = arduino.readline().decode('utf-8').rstrip()
                temp_value = float(raw_data)
                formatted_temp = f"{temp_value:.1f}"
                
                with data_lock:
                    app_data["temperature"] = formatted_temp
                
            except (UnicodeDecodeError, serial.SerialException) as e:
                print(f"Error reading from Arduino: {e}")
            except ValueError:
                print(f"Could not convert data to a number: '{raw_data}'")
        
        # We still sleep to prevent the thread from hogging the CPU
        time.sleep(0.1)


# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_temp')
def get_temp():
    with data_lock:
        response = jsonify(temperature=app_data["temperature"])
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# NEW: Route to stop the data reading
@app.route('/stop', methods=['POST'])
def stop_reading():
    global is_reading
    is_reading = False
    print("Stopping temperature reading.")
    return jsonify(status="stopped")


# --- Main Execution ---
if __name__ == '__main__':
    if not os.getenv('VERCEL_ENV'):
        arduino_thread = threading.Thread(target=read_from_arduino, daemon=True)
        arduino_thread.start()
        app.run(debug=True, use_reloader=False)
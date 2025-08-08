from flask import Flask, render_template, jsonify
import serial
import threading
import time

# --- Global Variables ---
app_data = {
    "temperature": "N/A" 
}
data_lock = threading.Lock()

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Background Thread for Reading Arduino Data ---
def read_from_arduino():
    """
    This function is now simplified to handle direct temperature values.
    """
    global app_data
    
    while True:
        try:
            # Make sure 'COM3' is still the correct port for your Arduino
            arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
            print("Arduino connected!")
            break
        except serial.SerialException:
            print("Arduino not found on COM3. Retrying in 5 seconds...")
            time.sleep(5)

    while True:
        if arduino.in_waiting > 0:
            try:
                # 1. Read the raw string from the serial port (e.g., "27.5")
                raw_data = arduino.readline().decode('utf-8').rstrip()
                
                # --- SIMPLIFIED LOGIC ---
                # 2. Directly convert the raw data string to a number.
                temp_value = float(raw_data)
                
                # 3. Format the number to one decimal place.
                formatted_temp = f"{temp_value:.1f}"
                
                # 4. Update the global variable.
                with data_lock:
                    app_data["temperature"] = formatted_temp
                
            except (UnicodeDecodeError, serial.SerialException) as e:
                print(f"Error reading from Arduino: {e}")
            except ValueError:
                # This still catches errors if the Arduino sends something non-numeric.
                print(f"Could not convert data to a number: '{raw_data}'")
                
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


# --- Main Execution ---
if __name__ == '__main__':
    arduino_thread = threading.Thread(target=read_from_arduino, daemon=True)
    arduino_thread.start()
    app.run(debug=True, use_reloader=False)
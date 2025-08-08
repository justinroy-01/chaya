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
# FIX #1: Corrected _name_ to __name__
app = Flask(__name__)

# --- Background Thread for Reading Arduino Data ---
def read_from_arduino():
    """
    This function now parses the string from the Arduino
    to extract the number we want.
    """
    global app_data
    
    while True:
        try:
            arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
            print("Arduino connected!")
            break
        except serial.SerialException:
            print("Arduino not found on COM3. Retrying in 5 seconds...")
            time.sleep(5)

    while True:
        if arduino.in_waiting > 0:
            try:
                # 1. Read the raw string: e.g., "Analog: 79 | Voltage: 0.39"
                raw_data = arduino.readline().decode('utf-8').rstrip()
                
                # FIX #2: --- ADDED PARSING LOGIC ---
                # This splits the string to grab just the analog value.
                value_str = raw_data.split(':')[1].split('|')[0].strip()
                # value_str is now a clean string like "79"

                # If you wanted the VOLTAGE instead, you would use this line:
                # value_str = raw_data.split('Voltage:')[1].strip()
                
                # --- END OF PARSING LOGIC ---

                # 3. Convert the extracted string ("79") to a number.
                temp_value = float(value_str)
                
                # 4. Format the number. (e.g., to one decimal place)
                formatted_temp = f"{temp_value:.1f}"
                
                # 5. Update the global variable with our final, clean data.
                with data_lock:
                    app_data["temperature"] = formatted_temp
                
            except (UnicodeDecodeError, serial.SerialException) as e:
                print(f"Error reading from Arduino: {e}")
            except (ValueError, IndexError) as e:
                # Catch errors if the string format is unexpected
                print(f"Could not parse data: '{raw_data}'. Error: {e}")
                
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
# FIX #1: Corrected _name_ and _main_ to __name__ and __main__
if __name__ == '__main__':
    arduino_thread = threading.Thread(target=read_from_arduino, daemon=True)
    arduino_thread.start()
    app.run(debug=True, use_reloader=False)
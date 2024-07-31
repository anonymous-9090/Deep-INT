import time
import mysql.connector
from datetime import datetime

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '123'
DB_NAME = 'network_data'
TABLE_NAME = 'network_packets'

def get_latest_timestamp():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT `timestamp` FROM {TABLE_NAME} ORDER BY `timestamp` DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result[0]
    return None

def get_current_epoch_time():
    return time.time()

def calculate_time_difference(db_timestamp):
    current_time = get_current_epoch_time()
    time_difference = current_time - db_timestamp
    return time_difference

def log_time_difference(difference):
    with open('difference.txt', 'a') as f:
        f.write(f"{difference}\n")

def log_sleep_interval(interval):
    with open('time1.txt', 'a') as f:
        f.write(f"{interval}\n")

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self._previous_error = 0
        self._integral = 0

    def update(self, measured_value, dt):
        error = self.setpoint - measured_value
        self._integral += error * dt
        derivative = (error - self._previous_error) / dt

        output = (self.Kp * error) + (self.Ki * self._integral) + (self.Kd * derivative)

        self._previous_error = error

        return output

# Modify the global sleep interval by writing to time.txt
def set_sleep_interval(interval):
    with open('time.txt', 'w') as f:
        f.write(str(interval))

if __name__ == '__main__':
    pid = PIDController(Kp=1, Ki=0.05, Kd=0.05, setpoint=0.1)

    # Wait for 3 seconds after starting
    time.sleep(3)

    while True:
        db_timestamp = get_latest_timestamp()
        if db_timestamp:
            time_difference = calculate_time_difference(db_timestamp)
            log_time_difference(time_difference)

            dt = 5  # Assuming we check every second
            new_interval = pid.update(time_difference, dt)
            new_interval = max(0.05, new_interval)  # Ensure interval is positive

            set_sleep_interval(new_interval)
            log_sleep_interval(new_interval)  # Log the interval to time1.txt
            print(f"Sleep interval set to {new_interval} seconds.")

        time.sleep(5)

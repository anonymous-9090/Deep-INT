import time
import mysql.connector

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

if __name__ == '__main__':
    while True:
        db_timestamp = get_latest_timestamp()
        if db_timestamp:
            time_difference = calculate_time_difference(db_timestamp)
            log_time_difference(time_difference)
            print(f"Logged time difference: {time_difference} seconds.")

        time.sleep(5)

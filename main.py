import serial
import mysql.connector
from mysql.connector import Error
import datetime

# Function to connect to MySQL database
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='rfid_database',
            user='root',
            password=''
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_info)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def handle_tag_scan(cursor, tag_id):
    # Check status is 'IN' or not
    cursor.execute("SELECT id FROM rfid_tags WHERE tag_id = %s AND status = 'IN'", (tag_id,))
    result = cursor.fetchone()

    if result:
        # Tag is exiting
        cursor.execute("UPDATE rfid_tags SET exit_time = %s, status = 'OUT' WHERE id = %s", (datetime.datetime.now(), result[0]))
        print(f"Tag ID {tag_id} marked as exited")
    else:
        # Tag is entering
        cursor.execute("INSERT INTO rfid_tags (tag_id, entry_time, status) VALUES (%s, %s, 'IN')", (tag_id, datetime.datetime.now()))
        print(f"Tag ID {tag_id} marked as entered")

    connection.commit()

# serial connection
try:
    ser = serial.Serial('COM3', 9600)
except serial.SerialException as e:
    print(f"Serial error: {e}")
    exit()

# Connect to MySQL database
connection = create_db_connection()
if connection is not None:
    cursor = connection.cursor()

    # Continuously read from the serial port and process data
    try:
        while True:
            if ser.in_waiting > 0:
                tag_id = ser.readline().decode('utf-8').rstrip()
                print(f"RFID Tag Scanned: {tag_id}")  # Print the scanned tag ID
                handle_tag_scan(cursor, tag_id)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()
        cursor.close()
        connection.close()
        print("Serial connection and MySQL connection are closed")
else:
    print("Failed to connect to the database.")

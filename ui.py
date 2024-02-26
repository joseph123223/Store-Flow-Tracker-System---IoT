import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import datetime

def update_time_label():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the time
    time_label.config(text=current_time)  # Update the label text
    root.after(1000, update_time_label)  # Schedule to update the label every second

def update_customer_list(force=False):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='rfid_database',
            user='root',
            password=''
        )
        cursor = connection.cursor()
        current_time = datetime.datetime.now()

        query = """
                SELECT tag_id, entry_time, status FROM rfid_tags
                WHERE status = 'IN' OR (status = 'OUT' AND exit_time > %s - INTERVAL 1 MINUTE)
                """
        cursor.execute(query, (current_time,))
        rows = cursor.fetchall()

        if force:
            tree.delete(*tree.get_children())

        # Clean the existing data when update
        for i in tree.get_children():
            tree.delete(i)

        for row in rows:
            tag_id, entry_time, status = row
            color = 'green' if status == 'IN' else 'red'
            tree.insert('', 'end', values=(tag_id, entry_time, status), tags=(color,))

        tree.tag_configure('green', background='#90EE90')
        tree.tag_configure('red', background='#FFCCCB')

        cursor.close()
        connection.close()
    except Error as e:
        print(f"Database error: {e}")

    root.after(1000, update_customer_list)  # Update every 1 seconds


root = tk.Tk()
root.title("Customer Status")

# Time Label setup
time_label = tk.Label(root, font=('Helvetica', 16))
time_label.pack()
update_time_label()  # Initial call to display the time

# Treeview setup
tree = ttk.Treeview(root, columns=('ID', 'Entry Time', 'Status'), show='headings')
tree.heading('ID', text='RFID Tag ID')
tree.heading('Entry Time', text='Entry Time')
tree.heading('Status', text='Status')
tree.pack(expand=True, fill='both')

# Initial update
update_customer_list()

root.mainloop()

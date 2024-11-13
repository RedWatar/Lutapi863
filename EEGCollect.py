import tkinter as tk
from tkinter import ttk, messagebox
import serial
import csv
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import threading
from collections import deque

# Serial Port Configuration
COM_PORT = 'COM11'
BAUD_RATE = 115200
SAMPLING_RATE = 250
WINDOW_SIZE = 500
eeg_data = deque([0] * WINDOW_SIZE, maxlen=WINDOW_SIZE)

# Initialize Serial Connection
ser = None

# Initialize Tkinter
root = tk.Tk()
root.title("NeuroGuard: EEG Data Collection")
root.geometry("800x600")

# Variables for Demographics
name_var = tk.StringVar()
age_var = tk.StringVar()
gender_var = tk.StringVar()
is_collecting = False

# Data Collection Functions
def start_data_collection():
    global is_collecting, ser
    is_collecting = True
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    filename = f"{name_var.get()}_{age_var.get()}_{gender_var.get()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    threading.Thread(target=collect_data, args=(filename,), daemon=True).start()

def stop_data_collection():
    global is_collecting, ser
    is_collecting = False
    ser.close()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    messagebox.showinfo("Info", "Data collection stopped and saved.")

def collect_data(filename):
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Timestamp", "EEG Value"])  # Write header
        start_time = time.time()
        while is_collecting and (time.time() - start_time < 300):  # Collect data for 5 minutes
            if ser.in_waiting > 0:
                data = ser.readline().decode("latin-1").strip()
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                if data.isdigit():
                    eeg_value = int(data)
                    eeg_data.append(eeg_value)
                    csvwriter.writerow([current_time, eeg_value])
                    update_graph()

def update_graph():
    plt.clf()
    plt.plot(list(eeg_data))
    plt.title("Real-Time EEG Data")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.pause(0.01)

# GUI for Data Collection
ttk.Label(root, text="Name:").pack()
name_entry = ttk.Entry(root, textvariable=name_var)
name_entry.pack()
ttk.Label(root, text="Age:").pack()
age_entry = ttk.Entry(root, textvariable=age_var)
age_entry.pack()
ttk.Label(root, text="Gender:").pack()
gender_entry = ttk.Entry(root, textvariable=gender_var)
gender_entry.pack()
start_button = ttk.Button(root, text="Start", command=start_data_collection)
start_button.pack(pady=10)
stop_button = ttk.Button(root, text="Stop", command=stop_data_collection, state=tk.DISABLED)
stop_button.pack(pady=10)

# Run the Application
plt.ion()
root.mainloop()

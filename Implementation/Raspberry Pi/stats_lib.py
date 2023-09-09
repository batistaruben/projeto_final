import time
import csv
import os
import shutil
from datetime import datetime
import csv
import sys

# Method that returns the current date in the "YYYY-MM-DD" format
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Method that returns the full path to the CSV file that stores temperature readings
# for the current day. The directory where files are stored is specified as an argument.
def temperature_data_file(data_directory):
    return os.path.join(data_directory, f"temperature_{get_current_date()}.csv")

# Similar to the previous method but for humidity
def humidity_data_file(data_directory):
    return os.path.join(data_directory, f"humidity_{get_current_date()}.csv")

# Similar to the previous method but for pH
def ph_data_file(data_directory):
    return os.path.join(data_directory, f"ph_{get_current_date()}.csv")

# Similar to the previous method but for water temperature
def water_temperature_data_file(data_directory):
    return os.path.join(data_directory, f"water_temperature_{get_current_date()}.csv")

# Similar to the previous method but for EC
def ec_data_file(data_directory):
    return os.path.join(data_directory, f"ec_{get_current_date()}.csv")

# This method receives a path to a CSV file and a value to be added to the file.
# It also checks if the value is not equal to zero and, if so, records the value
# along with a timestamp in the CSV file. It also sleeps for 1 second before returning.
def append_to_csv(file_path, value):
    if value != 0:  # Check if the value is not equal to 0
        timestamp = int(time.time())  # Current timestamp since the Unix epoch (January 1, 1970, at 00:00:00 UTC)
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, value])
            time.sleep(1)

# Creates a new CSV file at the specified path with a header consisting of
# "Timestamp" and "Value". This header is used to identify the columns in the CSV file.
def create_csv_with_header(file_path):
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Value"])

# This method creates a backup of CSV files in the current data directory (based on date) to a
# specified backup directory. The backup is created in a ZIP file named with the current date
# and contains all CSV data files from that day.
def create_backup(data_directory, backup_directory):
    current_date = get_current_date()
    backup_dir = os.path.join(backup_directory, current_date)

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backup_file = os.path.join(backup_dir, f"{current_date}_backup.zip")
    data_files = os.listdir(data_directory)

    for data_file in data_files:
        source_path = os.path.join(data_directory, data_file)
        destination_path = os.path.join(backup_dir, data_file)
        shutil.copy2(source_path, destination_path)

    shutil.make_archive(backup_file[:-4], "zip", backup_dir)
    print(f"Backup created: {backup_file}")

# This function reads data from a CSV file based on the specified parameter
# (e.g., temperature, humidity, pH) and date provided.
# It returns the read data as a list of lists, where each sublist contains
# a timestamp and a value.
def read_data(parameter, date):
    data = []
    try:
        # Generate the file name based on the parameter and date
        file_name = f'static/database/stats/data/{parameter}_{date}.csv'

        # Check if the file exists
        if not os.path.isfile(file_name):
            return data

        with open(file_name, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                timestamp = int(row['Timestamp'])
                value = float(row['Value'])
                data.append([timestamp, value])
    except Exception as e:
        print(f"An error occurred while reading the {parameter} CSV file for date {date}: {str(e)}")

    return data

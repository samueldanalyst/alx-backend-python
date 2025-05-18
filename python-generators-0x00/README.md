ALX_prodev Database Seeder
This project provides a Python script to set up a MySQL database named ALX_prodev with a table called user_data, and populates it with sample data from a CSV file. The script also includes a generator function to stream rows one by one from the database.

Features
Connects to MySQL server

Creates database ALX_prodev if it doesn’t exist

Creates user_data table with columns:

user_id (UUID, Primary Key, Indexed)

name (VARCHAR, NOT NULL)

email (VARCHAR, NOT NULL)

age (DECIMAL, NOT NULL)

Inserts data from user_data.csv if not already present

Provides a generator to stream database rows one by one

Requirements
Python 3.x

MySQL server installed and running

Python package: mysql-connector-python

Installation
Install Python dependencies

bash
Copy
Edit
pip install mysql-connector-python
Set up MySQL server

Make sure MySQL server is installed and accessible with your credentials.

Usage
Place your user_data.csv file in the project directory.

Run the main script (example file 0-main.py) which will:

Connect to MySQL

Create the database and table

Insert sample data from CSV

Verify the database and table content by printing sample rows

bash
Copy
Edit
python 0-main.py
Script Overview
seed.py contains:

connect_db(): Connects to MySQL server

create_database(connection): Creates ALX_prodev database if not exists

connect_to_prodev(): Connects to the ALX_prodev database

create_table(connection): Creates user_data table if not exists

insert_data(connection, csv_file): Reads CSV and inserts data if not exists

get_user_data_generator(connection): Generator that yields rows one by one from user_data


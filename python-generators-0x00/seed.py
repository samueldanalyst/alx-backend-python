import mysql.connector
import csv

# 1. Connect to MySQL server (without selecting a database)
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",  # <- Replace with your MySQL username
        password="your_password"  # <- Replace with your MySQL password
    )

# 2. Create the ALX_prodev database if it doesn't exist
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    connection.commit()
    cursor.close()

# 3. Connect directly to ALX_prodev database
def connect_to_prodev():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",  # <- Replace with your MySQL username
        password="your_password",  # <- Replace with your MySQL password
        database="ALX_prodev"
    )

# 4. Create the user_data table if it doesn't exist
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX(user_id)
        )
    """)
    connection.commit()
    cursor.close()
    print("Table user_data created successfully")

# 5. Insert data from CSV if it doesn't already exist
def insert_data(connection, data):
    cursor = connection.cursor()
    with open(data, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
            """, (row['user_id'], row['name'], row['email'], row['age']))
    connection.commit()
    cursor.close()

# BONUS: Generator to stream rows one by one from the database
def stream_rows(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    for row in cursor:
        yield row
    cursor.close()

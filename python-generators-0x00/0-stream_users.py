import mysql.connector

def stream_users():
    # Connect to the ALX_prodev database
    conn = mysql.connector.connect(
        host="localhost",
        user="your_mysql_user",
        password="your_mysql_password",
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True to get dict results
    
    # Execute query to select all rows from user_data
    cursor.execute("SELECT * FROM user_data")
    
    # Loop once over the cursor to yield rows one by one
    for row in cursor:
        yield row
    
    cursor.close()
    conn.close()

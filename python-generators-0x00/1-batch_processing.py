import mysql.connector

def stream_users_in_batches(batch_size):
    conn = mysql.connector.connect(
        host="localhost",
        user="your_mysql_user",
        password="your_mysql_password",
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user_data")
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    conn.close()

def batch_processing(batch_size):
    # Loop over batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25
        for user in batch:
            if user['age'] > 25:
                yield user

import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)  # open connection
        self.cursor = self.conn.cursor()
        return self.cursor  # return cursor to execute queries

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()  # commit if no exception
        else:
            self.conn.rollback()  # rollback if exception occurred
        self.cursor.close()
        self.conn.close()

# Example usage:
with DatabaseConnection('my_database.db') as cursor:
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    for row in results:
        print(row)

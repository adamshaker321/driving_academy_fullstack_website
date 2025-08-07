import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='HelloItsMeAdam$12',
        database='website_driving_academy'
    )
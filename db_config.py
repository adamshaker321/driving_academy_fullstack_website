import mysql.connector
from mysql.connector import pooling
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=32, 
    pool_reset_session=True,
    host='localhost',
    user='root',
    password='HelloItsMeAdam$12',
    database='website_driving_academy'
)
def get_connection():
    return connection_pool.get_connection()
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


_connection_pool = None

def get_connection(username, password):
    global _connection_pool
    if not _connection_pool:
		_connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=10, user = username, password = password, host='127.0.0.1', database='apiAccess') # MySQLConnection(**db_config)
    return _connection_pool

__all__ = [ 'getConnection' ]
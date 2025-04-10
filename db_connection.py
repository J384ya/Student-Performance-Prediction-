# db_connection.py

import pyodbc

def get_connection():
    driver = 'ODBC Driver 17 for SQL Server'
    server = 'DESKTOP-DUG0U2J\\SQLEXPRESS'
    database = 'StudentPerformanceDB'
    username = 'indus'
    password = 'Param@99811'

    conn_str = f"""
        DRIVER={{{driver}}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        Trust_Connection=no;
    """

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("✅ Connected to SQL Server successfully!")
        return conn, cursor
    except Exception as e:
        print("❌ Connection failed:", e)
        return None, None

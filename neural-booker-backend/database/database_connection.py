
import os
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import Error

load_dotenv()

dbHost = os.getenv('DB_HOST')
dbUser = os.getenv('DB_USER')
dbPassword = os.getenv('DB_PASSWORD')
databaseName = os.getenv('DB_DATABASE')
portNumber = os.getenv('DB_PORT')

def getDatabaseConnection():
    connection = None
    try:
        # Connect to the database
        connection = mysql.connector.connect(host=dbHost,user=dbUser,password=dbPassword,database=databaseName,port=portNumber)
        
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


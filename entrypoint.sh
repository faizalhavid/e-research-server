import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db(host, port):
    while True:
        try:
            # Attempt to connect to your database
            # Adjust the connection string to your database
            conn = psycopg2.connect(
                dbname='eresearchdb', user='postgres', password='220702', host=103.161.184.106, port=5432
            )
            print("Database is ready!")
            conn.close()
            break
        except OperationalError:
            print("Database is not ready, waiting...")
            time.sleep(1)

# Replace 'your_host' and 'your_port' with the appropriate variables or values
wait_for_db('103.161.184.106', 5432)
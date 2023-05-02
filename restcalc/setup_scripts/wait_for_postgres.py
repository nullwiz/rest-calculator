# Only used in docker

import os
import time
import psycopg2
connection_string = os.environ.get("DATABASE_URI")


def wait_for_postgres():
    while True:
        try:
            conn = psycopg2.connect(connection_string)
            conn.close()
            return
        except psycopg2.OperationalError as e:
            print(f"Unable to connect to PostgreSQL: {e}")
            time.sleep(1)


if __name__ == "__main__":
    wait_for_postgres()

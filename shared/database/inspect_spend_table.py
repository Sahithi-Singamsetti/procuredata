
from shared.database.connection import get_connection

connection = get_connection()

try:
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT *
            FROM spend_transactions
            LIMIT 10;
        """)

        # Display column names
        columns = [description[0] for description in cursor.description]

        print("\nCOLUMN NAMES:")
        print("-" * 80)
        for column in columns:
            print(column)

        # Display records
        rows = cursor.fetchall()

        print("\nFIRST 10 RECORDS:")
        print("-" * 80)

        for row in rows:
            print(row)

        # Display total record count
        cursor.execute("""
            SELECT COUNT(*)
            FROM spend_transactions;
        """)

        count = cursor.fetchone()[0]

        print("\nTOTAL RECORDS:", count)
        print("TOTAL COLUMNS:", len(columns))

finally:
    connection.close()

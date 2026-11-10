import duckdb


def main():
    # Step 1: Connect to a database file
    con = duckdb.connect(database="data/dd_events.duckdb")
    # Step 2: Create a new table from each JSON file
    con.execute("""
                CREATE TABLE raw_downtown AS
               SELECT *
               FROM read_json('data/raw/dd_events.json')
               """)
    con.execute("""
                CREATE TABLE raw_uptown AS
               SELECT *
               FROM read_json('data/raw/ut_events.json')
               """)
    # Step 3: Close the connection
    con.close()

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor

table = 'youtube_api'


def get_conn_cursor():
    """
    Get a connection and cursor to the Postgres database using Airflow's PostgresHook.
    
    Returns:
        conn: A connection object to the Postgres database.
        cursor: A cursor object for executing SQL queries.
    """
    # Create a PostgresHook instance
    hook = PostgresHook(postgres_conn_id='POSTGRES_DB_YT_ELT', database = 'Elt')
    
    # Get a connection from the hook
    conn = hook.get_conn()
    
    # Create a cursor with RealDictCursor to return results as dictionaries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    return conn, cursor


def close_conn_cursor(conn,cur):
    """
    Close the connection and cursor to the Postgres database.
    
    Args:
        conn: The connection object to the Postgres database.
        cursor: The cursor object for executing SQL queries.
    """
    cur.close()
    conn.close()


def create_schema(schema):
    """
    Create a schema in the Postgres database if it does not already exist.
    
    Args:
        schema: The name of the schema to create.
    """
    conn, cur = get_conn_cursor()
    
    # SQL query to create the schema if it doesn't exist
    create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
    
    # Execute the query
    cur.execute(create_schema_query)
    
    # Commit the changes
    conn.commit()
    
    # Close the connection and cursor
    close_conn_cursor(conn, cur)


def create_table(schema, table):
    """
    Create a table in the specified schema of the Postgres database if it does not already exist.
    
    Args:
        schema: The name of the schema where the table will be created.
        table: The name of the table to create.
    """
    conn, cur = get_conn_cursor()
    

    if schema == 'staging':
        # SQL query to create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            "Video_ID" VARCHAR(211) PRIMARY KEY NOT NULL,
            "Video_Title" TEXT NOT NULL,
            "Uploaded_Date" TIMESTAMP NOT NULL,
            "Duration" VARCHAR(20) NOT NULL,
            "Views_Count" BIGINT,
            "Likes_Count" BIGINT,
            "Comments_Count" BIGINT
        );
        """
    else:
        # SQL query to create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            "Video_ID" VARCHAR(211) PRIMARY KEY NOT NULL,
            "Video_Title" TEXT NOT NULL,
            "Uploaded_Date" TIMESTAMP NOT NULL,
            "Duration" TIME NOT NULL,
            "Video_Type" VARCHAR(20) NOT NULL,
            "Views_Count" BIGINT,
            "Likes_Count" BIGINT,
            "Comments_Count" BIGINT
        );
        """

    # Execute the query
    cur.execute(create_table_query)

    if schema != 'staging':
        cur.execute(
            f"""
            ALTER TABLE {schema}.{table}
            ADD COLUMN IF NOT EXISTS "Video_Type" VARCHAR(20);
            """
        )
    
    # Commit the changes
    conn.commit()
    
    # Close the connection and cursor
    close_conn_cursor(conn, cur)    


def get_video_ids(cur, schema):

    cur.execute(f"""select "Video_ID" from {schema}.{table}""")
    ids = cur.fetchall()

    video_ids = [row["Video_ID"] for row in ids]

    return video_ids



import logging

logger = logging.getLogger(__name__)
table = "youtube_api"


def insert_rows(cur,conn,schema,row):
    """
    Insert a row into the specified schema and table.

    Args:
        cur: The database cursor.
        conn: The database connection.
        schema: The schema name where the table is located.
        row: A dictionary containing the row data to insert.
    """
    try:
        if schema == 'staging':

            video_id = 'video_id'

            cur.execute(
                f"""INSERT INTO {schema}.{table} ("Video_ID", "Video_Title", "Uploaded_Date", "Duration", "Views_Count", "Likes_Count", "Comments_Count")
                    VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s)
                """
                , row
            ) 

        else:

            video_id = 'Video_ID'

            cur.execute(
                f"""INSERT INTO {schema}.{table} ("Video_ID", "Video_Title", "Uploaded_Date", "Duration", "Video_Type", "Views_Count", "Likes_Count", "Comments_Count")
                    VALUES (%(Video_ID)s, %(Video_Title)s, %(Uploaded_Date)s, %(Duration)s, %(Video_Type)s, %(Views_Count)s, %(Likes_Count)s, %(Comments_Count)s);
                """
                , row
            )
        
        conn.commit()
        
        logger.info(f"Inserted row with Video_ID {row[video_id]} ")

    except Exception as e:
        logger.error(f"Error inserting row into {schema}.{table}: {e}")
        raise e


def update_rows(cur,conn,schema,row):  
    """
    Update rows in the specified schema and table based on a list of video IDs.

    Args:
        cur: The database cursor.
        conn: The database connection.
        schema: The schema name where the table is located.
        ids_to_update: A list of video IDs to update in the table.
    """

    try:
        #staging
        if schema == 'staging':
            video_id = 'video_id'
            cur.execute(
                f"""UPDATE {schema}.{table}
                    SET "Video_Title" = %(title)s,
                        "Uploaded_Date" = %(publishedAt)s,
                        "Duration" = %(duration)s,
                        "Views_Count" = %(viewCount)s,
                        "Likes_Count" = %(likeCount)s,
                        "Comments_Count" = %(commentCount)s
                    WHERE "Video_ID" = %(video_id)s;
                """
                , row
            )
        #core
        else: 
            video_id = 'Video_ID'
            cur.execute(
                f"""UPDATE {schema}.{table}
                    SET "Video_Title" = %(Video_Title)s,
                        "Uploaded_Date" = %(Uploaded_Date)s,
                        "Duration" = %(Duration)s,
                        "Video_Type" = %(Video_Type)s,
                        "Views_Count" = %(Views_Count)s,
                        "Likes_Count" = %(Likes_Count)s,
                        "Comments_Count" = %(Comments_Count)s
                    WHERE "Video_ID" = %(Video_ID)s;
                """
                , row
            )

        conn.commit()

        logger.info(f"Updated row with Video_ID {row[video_id]} ")

    except Exception as e:
        logger.error(f"Error updating row with Video_ID {row[video_id]} in {schema}.{table}: {e}")
        raise e
    

def delete_rows(cur, conn, schema, ids_to_delete):
    """
    Delete rows from the specified schema and table based on a list of video IDs.

    Args:
        cur: The database cursor.
        conn: The database connection.
        schema: The schema name where the table is located.
        ids_to_delete: A list of video IDs to delete from the table.
    """
    try:
        # Define the ids to delete in a format suitable for SQL query
        delete_query = f"""DELETE FROM {schema}.{table} WHERE "Video_ID" = ANY(%s);"""
        cur.execute(delete_query, (list(ids_to_delete),))
        
        # Commit the changes to the database
        conn.commit()
        
        logger.info(f"Deleted rows with Video_IDs {ids_to_delete} from {schema}.{table}")

    except Exception as e:
        logger.error(f"Error deleting rows with Video_IDs: {ids_to_delete} from {schema}.{table}: {e}")
        raise e


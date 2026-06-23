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
                f"""INSERT INTO {schema}.{table} (Video_ID, Video_Title, Uploaded_Date, Duration, Video_Views, Like_Count, Comment_Count) 
                    VALUES (%(video_id)s, %(title)s, %(published_at)s, %(duration)s, %(viewcount)s, %(likecount)s, %(commentcount)s)
                """
                , row
            ) 

        else:

            video_id = 'Video_ID'

            cur.execute(
                f"""INSERT INTO {schema}.{table} (Video_ID, Video_Title, Uploaded_Date, Duration, Video_Views, Like_Count, Comment_Count) 
                    VALUES (%(Video_ID)s, %(Video_Title)s, %(Uploaded_Date)s, %(Duration)s, %(Video_Views)s, %(Likes_Count)s, %(Comments_Count)s);
                """
                , row
            )
        
        conn.commit()
        
        logger.info(f"Inserted row with Video_ID {row['video_id']} ")

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
            uploaded_date = 'published_at'
            title = 'title'
            video_views = 'viewcount'
            like_count = 'likecount'
            comment_count = 'commentcount'
        #core
        else: 
            video_id = 'Video_ID'
            uploaded_date = 'Uploaded_Date'
            title = 'Video_Title'
            video_views = 'Video_Views'
            like_count = 'Likes_Count'
            comment_count = 'Comments_Count'

        cur.execute(
            f"""UPDATE {schema}.{table} 
                SET "Video_Title" = %(video_title)s, 
                    "Video_Views" = %(video_views)s, 
                    "Likes_Count" = %(likes_count)s, 
                    "Comments_Count" = %(comments_count)s
                WHERE "Video_ID" = %(video_id)s and "Uploaded_Date" = %(uploaded_date)s;
            """
            , row
        )

        conn.commit()

        logger.info(f"Updated row with Video_ID {row['video_id']} ")

    except Exception as e:
        logger.error(f"Error updating row with Video_ID {row['video_id']} in {schema}.{table}: {e}")
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
        ids_to_delete = f"""({', '.join(f"'{id}'" for id in ids_to_delete)})"""
        # Prepare the SQL query for deletion
        delete_query = f"DELETE FROM {schema}.{table} WHERE 'Video_ID' IN {ids_to_delete};"
        
        # Execute the deletion query
        cur.execute(delete_query)
        
        # Commit the changes to the database
        conn.commit()
        
        logger.info(f"Deleted rows with Video_IDs {ids_to_delete} from {schema}.{table}")

    except Exception as e:
        logger.error(f"Error deleting rows with Video_IDs: {ids_to_delete} from {schema}.{table}: {e}")
        raise e


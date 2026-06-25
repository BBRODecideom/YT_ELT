from datawarehouse.data_utils import get_conn_cursor, close_conn_cursor, create_schema, create_table, get_video_ids
from datawarehouse.data_loading import load_path
from datawarehouse.data_modification import insert_rows, update_rows, delete_rows
from datawarehouse.data_transformation import transform_data

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table = "youtube_api"


@task
def stagging_table():

    schema = 'staging'

    conn, cur = None, None

    try:
        
        conn, cur = get_conn_cursor()

        YT_data = load_path()

        create_schema(schema)
        create_table(schema, table)

        table_ids = get_video_ids(cur,schema)
        ids_in_json = {row['video_id'] for row in YT_data}

        for row in YT_data:

            if len(table_ids) == 0:

                insert_rows(cur,conn,schema,row)
            
            else:

                if row['video_id'] in table_ids:
                    update_rows(cur,conn,schema,row)
                else:
                    insert_rows(cur,conn,schema,row)

        ids_to_delete = set(table_ids) - ids_in_json

        if ids_to_delete:
            delete_rows(cur,conn,schema,ids_to_delete)

        logger.info(f"{schema} table update completed")

    except Exception as e:
        logger.error(f" An error occured during the update of {schema} table {e}")    
        raise e
    
    finally:
        if conn and cur:
                close_conn_cursor(conn,cur)
        

@task
def core_table():

    schema = 'core'

    conn, cur = None, None

    try:
        
        conn, cur = get_conn_cursor()

        create_schema(schema)
        create_table(schema, table)

        table_ids = get_video_ids(cur,schema)

        current_video_ids = set()

        # Fix error on table already exist
        cur.execute(f"DROP TABLE IF EXISTS core.{table}_rejected;")
        cur.execute(f"DROP TABLE IF EXISTS core.{table};")

        # 1. Gestion des rejets (Création de la table directement en SQL)
        cur.execute(f"""
                    CREATE TABLE core.{table}_rejected AS
                    SELECT *
                    FROM staging.{table}
                    WHERE "Comments_Count" > "Views_Count";
                """)

        # 2. S'assurer que la table principale existe (SANS LA DROP)
        # S'il s'agit du premier run, elle sera créée avec la même structure que la table staging
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS core.{table} 
            (LIKE staging.{table} INCLUDING ALL);
        """)
        cur.execute(f"""
            ALTER TABLE core.{table}
            ADD COLUMN IF NOT EXISTS "Video_Type" VARCHAR(255);
        """)

        # 3. Récupération des données VALIDES pour le traitement Python
        # On utilise un SELECT classique, donc fetchall() va fonctionner
        #cur.execute(f"""CREATE TABLE core.{table} AS SELECT * FROM staging.{table} WHERE "Comments_Count" <= "Views_Count";""")
        cur.execute(f"""SELECT * FROM staging.{table} WHERE "Comments_Count" <= "Views_Count";""")
        rows = cur.fetchall()
        # Pour obtenir le nombre de lignes insérées dans la dernière table créée :
        row_updated = cur.rowcount
        print(f"This is the number of ligne updated in core.{table} : {len(rows)}")

        # 4. Application de ta logique d'origine sur les lignes récupérées
        for row in rows:
            transformed_row = transform_data(row)
            current_video_ids.add(transformed_row['Video_ID'])

            if transformed_row['Video_ID'] in table_ids:
                update_rows(cur,conn,schema,transformed_row)
            else:
                insert_rows(cur,conn,schema,transformed_row)

        ids_to_delete = set(table_ids) - current_video_ids

        if ids_to_delete:
            delete_rows(cur,conn,schema,ids_to_delete)

        logger.info(f"{schema} table update completed")

    except Exception as e:
        logger.error(f" An error occured during the update of {schema} table {e}")    
        raise e
    
    finally:
        if conn and cur:
                close_conn_cursor(conn,cur)

    

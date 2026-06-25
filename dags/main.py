from airflow import DAG
import pendulum
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json
from datawarehouse.data_warehouse import stagging_table, core_table
from dataquality.soda import youtube_elt_data_quality

#Default time
local_tz = pendulum.timezone("Europe/Paris")

#Default args
default_args = {

    "owner" : "dataengineers",
    "depends_on_past" : False,
    "email_on_failure" : False,
    "email_on_retry" : False,
    "email" : "data@enginners.com",
    #"retries" : 1,
    #"retry_delay" : timedelta(minutes=5),
    "max_active_runs" : 1,
    "dag_run_timeout" : timedelta(minutes=60),
    "start_date": datetime(2026, 1, 1, tzinfo=local_tz),
    #"end_date": datetime(2026, 7, 1, tzinfo=local_tz),

}

# Define core variables
staging_schema = "staging"
core_schema = "core"


with DAG(

    dag_id='produce_json',
    default_args=default_args,
    description= 'DAG to produce json file with raw data from youtube api',
    schedule='0 14 * * *',
    catchup=False

) as dag_produce:


    #DEFINE TASKS
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extract_data = extract_video_data(video_ids)
    save_to_json_task = save_to_json(extract_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db"
    )

    #DEFINE DEPENDENCIES
    playlist_id >> video_ids >> extract_data >> save_to_json_task >> trigger_update_db


with DAG(

    dag_id='update_db',
    default_args=default_args,
    description= 'DAG to process json file and insert data into both stagging and core schema',
    schedule=None,
    catchup=False

) as dag_update:


    #DEFINE TASKS
    update_staging = stagging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality"
    )

    #DEFINE DEPENDENCIES
    update_staging >> update_core >> trigger_data_quality


with DAG(

    dag_id='data_quality',
    default_args=default_args,
    description= 'DAG to check data quality on both layer in the db',
    schedule=None,
    catchup=False

) as dag_quality:


    #DEFINE TASKS
    soda_validate_staging = youtube_elt_data_quality(staging_schema, trigger_rule="all_done")
    soda_validate_core = youtube_elt_data_quality(core_schema, trigger_rule="all_done") 

    #DEFINE DEPENDENCIES
    soda_validate_staging >> soda_validate_core 


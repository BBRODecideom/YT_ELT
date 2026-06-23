import json
from datetime import date
import logging

logger = logging.getLogger(__name__)


def load_path():

    file_path = f"./data/YT_Data_{date.today()}.json"

    try:
        logger.info(f"Loading data from {file_path}") 

        with open(file_path, 'r', encoding = 'utf-8') as json_file:
            data = json.load(json_file)
            logger.info(f"Data loaded successfully from {file_path}")
            return data
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise   
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise



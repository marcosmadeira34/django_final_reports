import logging

logger = logging.getLogger('celery')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('celery.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
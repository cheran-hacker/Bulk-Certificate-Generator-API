import logging
from app.core.config import settings

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

import logging
import logging.config
from logging.handlers import RotatingFileHandler
import gfss_parameter as cfg
import app_config as cfg_app
from app_config import debug_level


def init_logger():
    logger = logging.getLogger('REPORTS-GFSS')
    # logging.getLogger('PDD').addHandler(logging.StreamHandler(sys.stdout))
    # Console
    logging.getLogger('GFSS-REGISTRY').addHandler(logging.StreamHandler())
    if debug_level>2:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    fh = logging.FileHandler(f"{cfg_app.LOG_PATH}/{cfg.app_name.lower()}.log", encoding="UTF-8")
    # fh = RotatingFileHandler(cfg.LOG_FILE, encoding="UTF-8", maxBytes=100000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.info('GFSS-REGISTRY Logging started')
    return logger


log = init_logger()
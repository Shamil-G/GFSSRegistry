import logging
import logging.config
from logging.handlers import RotatingFileHandler
from gfss_parameter import debug
import app_config as cfg_app


def init_logger():
    logger = logging.getLogger('GFSS-REGISTRY')
    # logging.getLogger('PDD').addHandler(logging.StreamHandler(sys.stdout))
    # Console
    logging.getLogger('GFSS-REGISTRY').addHandler(logging.StreamHandler())
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    fh = logging.FileHandler(f"{cfg_app.LOG_PATH}/gfss-registry.log", encoding="UTF-8")
    # fh = RotatingFileHandler(cfg.LOG_FILE, encoding="UTF-8", maxBytes=100000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.info(f'GFSS-REGISTRY Logging started with debug={debug}')
    return logger


log = init_logger()
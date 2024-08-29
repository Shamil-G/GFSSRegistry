from __init__ import app
import app_config as cfg
from util.logger import log
from db.user_login import * 
from view.routes import *


if __name__ == "__main__":
    log.info(f"===> Main REPORTS-GFSS started on {cfg.host}:{cfg.port}, work_dir: {cfg.BASE}")
    app.run(host=cfg.host, port=cfg.port, debug=False)

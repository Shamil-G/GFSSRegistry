from gfss_parameter import app_name

from flask import Flask
from util.logger import log
from flask_session import Session

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'GFSSRegistry sk: ;lsjagsdna4ldyw2kag5y91sd'
# app.secret_key = 'this is secret key qer:ekjf;keriutype2tO287'
#app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])
app.config.from_object('db_config.SessionConfig')
server_session = Session(app)
log.info(f'GFSSRegistry configured and started')

log.info(f"__INIT MAIN APP for {app_name} started")
print("__INIT MAIN APP__ started")

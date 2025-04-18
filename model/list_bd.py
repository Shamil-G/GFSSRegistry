from app_config import sso_server
from main_app import log
import requests

def get_list_birthdate():
    resp_data = []
    resp = requests.get(f'{sso_server}/bd')
    log.debug(f'GET LIST BIRTHDATE\n\tSSO SERVER: {sso_server}\n\tRESP: {resp}')
    # for r in resp:
    #     log.debug(f'GET LIST BIRTHDATE. R: {r.decode}')

    if resp.status_code == 200:
        resp_data=resp.json()
        log.debug(f'GET LIST BIRTHDATE. resp_data: {resp_data}')

    return resp_data
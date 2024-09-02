from app_config import URL_LOGIN, debug_level
from gfss_parameter import public_name
from main_app import log
from db.connect import get_connection
import requests


def get_user_roles(username, passwd, ip):
    request_json = { "app_name": public_name, "username": username, "passwd": passwd, "ip_addr": ip }
    url = f'{URL_LOGIN}/get-roles'
    try:
        resp = requests.post(url, json=request_json)
        status = resp.status_code
        if status == 200:
            if debug_level > 2:
                log.info(f'-----> GET USER ROLES. resp: {resp}, status: {status}, request_json: {request_json}')
            resp_json = resp.json()
        else:
            log.error(f'\nERROR GET USER ROLES. "username": {username}, URL: {url}, status: {status}')
            resp_json = {"status": 'ERROR', "username": username, "roles": [], "mess": f'RESP STATUS: {status}'}
    except requests.exceptions.HTTPError as errH:
        log.error(f"=====> Http Error. request get-roles. username: {username} : {errH}")
        resp_json = {"mistake": f'{errH}', "username": username, "roles": []}
    except requests.exceptions.Timeout as errT:
        log.error(f'=====> TIMEOUT ERROR. request get-roles. username: {username} : {errT}')
        resp_json = {"mistake": f'{errT}', "username": username, "roles": []}
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'=====> ERROR MANY REDIRECT. request get-roles. username: {username} : {errM}')
        resp_json = {"mistake": f'{errM}', "username": username, "roles": []}
    except requests.exceptions.ConnectionError as errC:
        log.error(f'=====> ERROR CONNECTION. request get-roles. username: {username} : {errC}')
        resp_json = {"mistake": f'{errC}', "username": username, "roles": []}
    except requests.exceptions.RequestException as errE:
        log.error(f'=====> REQUEST ERROR. request get-roles. username: {username} : {errE}')
        resp_json = {"mistake": f'{errE}', "username": username, "roles": []}
    except Exception as e:
        log.error(f'---> GET USER ROLES. URL: {url}, ERROR: {e}')
        resp_json = {"mistake": f'{e}', "username": username, "roles": []}
    finally:
        if debug_level > 2:
            log.info(f"GET ROLES. FINALLY. USERNAME: {username}, resp_json: {resp_json}")
        return resp_json


def change_passwd(username, passwd, new_passwd):
    request_json = { "app_name": public_name, "username": username, "passwd": passwd, "new_passwd": new_passwd }
    url = f'{URL_LOGIN}/change-passwd'
    try:
        resp = requests.post(url, json=request_json)
        status = resp.status_code
        if status == 200:
            if debug_level > 2:
                log.info(f'-----> GET CHANGE PASSWORD. resp: {resp}, status: {status}, request_json: {request_json}')
            resp_json = resp.json()
        else:
            log.error(f'\nERROR CHANGE PASSWORD. "username": {username}, URL: {url}, status: {status}')
            resp_json = {"mistake": '100', "username": username, "mess": f'RESP STATUS: {status}'}
    except requests.exceptions.HTTPError as errH:
        log.error(f"\n=====> Http Error. request change-password. username: {username} : {errH}")
        resp_json = {"mistake": f'{errH}', "username": username, "roles": []}
    except requests.exceptions.Timeout as errT:
        log.error(f'\n=====> TIMEOUT ERROR. request change-password. username: {username} : {errT}')
        resp_json = {"mistake": f'{errT}', "username": username, "roles": []}
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'\n=====> ERROR MANY REDIRECT. request change-password. username: {username} : {errM}')
        resp_json = {"mistake": f'{errM}', "username": username, "roles": []}
    except requests.exceptions.ConnectionError as errC:
        log.error(f'\n=====> ERROR CONNECTION. request change-password. username: {username} : {errC}')
        resp_json = {"mistake": f'{errC}', "username": username, "roles": []}
    except requests.exceptions.RequestException as errE:
        log.error(f'\n=====> REQUEST ERROR. request change-password. username: {username} : {errE}')
        resp_json = {"mistake": f'{errE}', "username": username, "roles": []}
    except Exception as e:
        log.error(f'=====> GET CHANGE PASSWORD. URL: {url}, ERROR: {e}')
        resp_json = {"mistake": f'{e}', "username": username, "roles": []}
    finally:
        if debug_level > 2:
            log.info(f"CHANGE PASSWORD. FINALLY. USERNAME: {username}, resp_json: {resp_json}")
        return resp_json


def user_info(username):
    request_json = { "app_name": public_name, "username": username }
    url = f'{URL_LOGIN}/user-info'
    try:
        resp = requests.post(url, json=request_json)
        status = resp.status_code
        if status == 200:
            if debug_level > 2:
                log.info(f'-----> GET CHANGE PASSWORD. resp: {resp}, status: {status}, request_json: {request_json}')
            resp_json = resp.json()
        else:
            log.error(f'\nERROR GET USER INFO. "username": {username}, URL: {url}, status: {status}')
            resp_json = {"mistake": 'ERROR', "username": username, "mess": f'RESP STATUS: {status}'}
    except requests.exceptions.HTTPError as errH:
        log.error(f"=====> Http Error. request user-info. username: {username} : {errH}")
        resp_json = {"mistake": f'{errH}', "username": username, "roles": []}
    except requests.exceptions.Timeout as errT:
        log.error(f'=====> TIMEOUT ERROR. request user-info. username: {username} : {errT}')
        resp_json = {"mistake": f'{errT}', "username": username, "roles": []}
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'=====> ERROR MANY REDIRECT. request user-info. username: {username} : {errM}')
        resp_json = {"mistake": f'{errM}', "username": username, "roles": []}
    except requests.exceptions.ConnectionError as errC:
        log.error(f'=====> ERROR CONNECTION. request user-info. username: {username} : {errC}')
        resp_json = {"mistake": f'{errC}', "username": username, "roles": []}
    except requests.exceptions.RequestException as errE:
        log.error(f'=====> REQUEST ERROR. request user-info. username: {username} : {errE}')
        resp_json = {"mistake": f'{errE}', "username": username, "roles": []}
    except Exception as e:
        log.error(f'=====> ERROR. request user-info. URL: {url}, ERROR: {e}')
        resp_json = {"mistake": f'{e}', "username": username, "roles": []}
    finally:
        if debug_level > 2:
            log.info(f"REQUEST USER INFO. FINALLY. USERNAME: {username}, resp_json: {resp_json}")
        return resp_json


def server_logout(id_user):
    request_json = { "id_user": id_user}
    url = f'{URL_LOGIN}/user--logout'
    try:
        resp = requests.post(url, json=request_json)
        status = resp.status_code
        if status == 200:
            if debug_level > 2:
                log.info(f'-----> USER LOGOUT. resp: {resp}, status: {status}, request_json: {request_json}')
            resp_json = resp.json()
        else:
            log.error(f'\nERROR GET USER INFO. "id_user": {id_user}, URL: {url}, status: {status}')
            resp_json = {"mistake": 'ERROR', "id_user": {id_user}, "mess": f'RESP STATUS: {status}'}
    except requests.exceptions.HTTPError as errH:
        log.error(f"=====> Http Error. request user-info. id_user: {id_user} : {errH}")
        resp_json = {"mistake": f'{errH}', "id_user": {id_user}, "roles": []}
    except requests.exceptions.Timeout as errT:
        log.error(f'=====> TIMEOUT ERROR. request user-info. "id_user": {id_user} : {errT}')
        resp_json = {"mistake": f'{errT}', "id_user": {id_user}, "roles": []}
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'=====> ERROR MANY REDIRECT. request user-info. "id_user": {id_user} : {errM}')
        resp_json = {"mistake": f'{errM}', "id_user": {id_user}, "roles": []}
    except requests.exceptions.ConnectionError as errC:
        log.error(f'=====> ERROR CONNECTION. request user-info. "id_user": {id_user} : {errC}')
        resp_json = {"mistake": f'{errC}', "id_user": {id_user}, "roles": []}
    except requests.exceptions.RequestException as errE:
        log.error(f'=====> REQUEST ERROR. request user-info. "id_user": {id_user} : {errE}')
        resp_json = {"mistake": f'{errE}', "id_user": {id_user}, "roles": []}
    except Exception as e:
        log.error(f'=====> ERROR. request user-info. URL: {url}, ERROR: {e}')
        resp_json = {"mistake": f'{e}', "id_user": {id_user}, "roles": []}
    finally:
        if debug_level > 2:
            log.info(f"REQUEST USER INFO. FINALLY. id_user: {id_user}, resp_json: {resp_json}")
        return resp_json


def add_time_off(date_out:str, date_in:str, employee:str, post:str, dep_name:str, cause:str, head_name:str):
    stmt = """
        insert into register(time_out, time_in, employee, post, dep_name, cause, head)
        values(to_date(:time_out,'YYYY-MM-DD HH24:MI'), 
                to_date(:time_in,'YYYY-MM-DD HH24:MI'), 
                :employee, :post, :dep_name, :cause, :head_name
                )
    """
    success = 0
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, time_out=date_out, time_in=date_in, 
                               employee=employee,
                               post=post,
                               dep_name=dep_name,
                               cause=cause, head_name=head_name)
                cursor.execute('commit')
                success = 1
            finally:
                log.info('TIME_OFF. executed')
    return success

def get_list_head():
    list_head = []
    stmt = """
        select id_head, name from heads order by id_head
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'id_head': row[0], 'head_name': row[1]}
                    list_head.append(res)
            finally:
                if debug_level > 2:
                    log.info(f'LIST HEAD. {list_head}')
    return list_head

def add_head(head_name: str):
    stmt = """
        begin admin.add_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.info(f'ADD HEAD. {head_name}')
    
def del_head(head_name: str):
    stmt = """
        begin admin.del_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.info(f'DEL HEAD. {head_name}')
    

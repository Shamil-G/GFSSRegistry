from app_config import debug_level
from main_app import log
from db.connect import get_connection, plsql_func_s


def add_time_off(date_out:str, date_in:str, employee:str, post:str, dep_name:str, cause:str, head_name:str):
    args = [date_out, date_in, employee, post, dep_name, cause, head_name]
    log.debug(f"ADD_TIME_OFF. args: {args}")    
    result = plsql_func_s('Регистрация времени отсутствия', 'reg.add_reg', args)    
    return result


def get_list_time_off(employee: str):
    list_time_off = []
    
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, id 
        from register r
        where r.employee = :employee
        order by event_date desc
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, employee=employee)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'id': row[8]
                           }
                    list_time_off.append(res)
            finally:
                log.debug(f'LIST HEAD. {list_time_off}')
    return list_time_off


def get_list_absent():
    list_absent = []
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, id 
        from register r
        where sysdate between time_out and time_in
        order by event_date desc
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'id': row[8]
                           }
                    list_absent.append(res)
            finally:
                log.debug(f'LIST ABSENT. {list_absent}')
    return list_absent


def get_all_list_time_off(mnth: str):
    list_time_off = []
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, id 
        from register r
        where trunc(event_date,'MM') = trunc(to_date(:mnth,'YYYY-MM-DD'),'MM')
        order by event_date desc
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, mnth=mnth)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'id': row[8]
                           }
                    list_time_off.append(res)
            finally:
                log.debug(f'LIST HEAD. {list_time_off}')
    return list_time_off


def get_list_to_approve(dep_name):
    list_approve = []
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, id 
        from register r
        where trunc(event_date,'MM') = trunc(sysdate,'MM')
        and   dep_name = :dep_name
        order by event_date desc
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                log.debug(f'LIST APPROVE. dep_name: {dep_name} : {type(dep_name)}')
                cursor.execute(stmt, dep_name=dep_name)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'id': row[8]
                           }
                    list_approve.append(res)
            finally:
                log.debug(f'LIST APPROVE. {list_approve}')
    return list_approve


def del_time_off(id_reg: int, employee: str):
    stmt = """
        begin reg.del_time_off(:id_reg); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, id_reg=id_reg)
            finally:
                log.info(f'DEL TIME_OFF. username: {employee}, id_reg: {id_reg}')


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


def approve_time_off(id_reg: int, boss: str):
    stmt = """
        begin reg.approve_time_off(:id_reg, :boss); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, id_reg=id_reg, boss=boss)
            finally:
                log.info(f'DEL TIME_OFF. boss: {boss}, id_reg: {id_reg}')


def add_head(head_name: str):
    stmt = """
        begin reg.add_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.info(f'ADD HEAD. {head_name}')

    
def del_head(head_name: str):
    stmt = """
        begin reg.del_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.info(f'DEL HEAD. {head_name}')

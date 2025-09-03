from main_app import log
from db.connect import get_connection, plsql_func_s


def add_time_off(date_out:str, date_in:str, employee:str, post:str, dep_name:str, cause:str):
    args = [date_out, date_in, employee, post, dep_name, cause]
    log.debug(f"ADD_TIME_OFF. args: {args}")    
    result = plsql_func_s('Регистрация времени отсутствия', 'reg.add_reg', args)    
    return result


def add_secure_time_off(date_out:str, date_in:str, employee:str, post:str, dep_name:str, cause:str, boss:str):
    args = [date_out, date_in, employee, post, dep_name, cause, boss]
    log.info(f"ADD_SECURE_TIME_OFF. args: {args}")    
    result = plsql_func_s('Регистрация времени отсутствия', 'reg.add_secure_reg', args)    
    return result


def get_list_time_off(employee: str):
    list_time_off = []
    
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, time_fact,
               sysdate - trunc(time_out,'MM') as cnt_days, status, id
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
                    res = {'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 
                           'status': row[8], 'time_fact': row[9], 
                           'cnt_days': row[10], 'sttaus': row[11], 'id': row[12], 
                           }
                    list_time_off.append(res)
            finally:
                log.debug(f'LIST HEAD. {list_time_off}')
    return list_time_off


def get_list_absent():
    list_absent = []
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, id 
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
                           'cause': row[6], 'head': row[7], 'status': row[8], 'id': row[9]
                           }
                    list_absent.append(res)
            finally:
                log.debug(f'LIST ABSENT. {list_absent}')
    return list_absent


def get_all_list_time_off(boss_adm, mnth: str):
    list_time_off = []

    if boss_adm.is_anonymous():
        log.info(f'GET_LIST_TO_APPROVE: USER is ANONYMOUS')
        return {}

    admin = 0 # Администратор, служба безопасности
    boss = 0  # Руководитель департамента
    subordinate_ou = ""
    if hasattr(boss_adm, 'subordinate_ou') and boss_adm.subordinate_ou is not None:
        subordinate_ou = ", ".join( f"'{str(elem)}'" for elem in boss_adm.subordinate_ou)

    if hasattr(boss_adm, 'roles'):
        if 'admin' in boss_adm.roles:
            admin=1
        if 'boss' in boss_adm.roles:
            boss=1

    if admin==1:
        stmt = """
            select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, id  
            from register r
            where trunc(event_date,'MM') = trunc(to_date(':mnth','YYYY-MM-DD'),'MM')
            order by event_date desc
        """
    else:
        stmt = """
            select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, id
            from register r
            where trunc(event_date,'MM') = trunc(to_date(':mnth','YYYY-MM-DD'),'MM')
            and   dep_name in (:dep_name)
            order by event_date desc
        """
    
    stmt_1 = stmt.replace(':mnth', mnth);
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                stmt_list=stmt_1
                if subordinate_ou and subordinate_ou is not None:
                    stmt_list = stmt_1.replace(':dep_name', subordinate_ou);
                elif boss==1:
                    stmt_list = stmt_1.replace(':dep_name', f"'{boss_adm.dep_name}'")

                log.info(f'-------\n\tGET ALL LIST TIME_ OFF. STMT:\n\t{stmt_list}-------')
                cursor.execute(stmt_list)
                rows = cursor.fetchall()

                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'status': row[8], 'id': row[9]
                           }
                    list_time_off.append(res)
            finally:
                log.debug(f'GET ALL LIST TIME_ OFF. {list_time_off}')
    return list_time_off, stmt_list


def get_list_to_approve(user):
    if user.is_anonymous():
        log.info(f'GET_LIST_TO_APPROVE: USER is ANONYMOUS')
        return {}

    admin = 0 # Администратор, служба безопасности
    boss = 0  # Руководитель департамента
    subordinate_ou = ""
    if hasattr(user, 'subordinate_ou') and user.subordinate_ou is not None:
        subordinate_ou = ", ".join( f"'{str(elem)}'" for elem in user.subordinate_ou)

    if hasattr(user, 'roles'):
        if 'admin' in user.roles:
            admin=1
        if 'boss' in user.roles:
            boss=1

    log.info(f'GET_LIST_TO_APPROVE. Admin: {admin}, Boss: {boss}')

    if admin==1:
        stmt = """
            select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, id 
            from register r
            where trunc(event_date,'MM') >= trunc(sysdate,'MM')-5
            and   status = 0
            order by event_date desc
        """
    else:
        stmt = """
            select event_date, time_out, time_in, employee, post, dep_name, cause, head, status, id 
            from register r
            where trunc(event_date,'MM') >= trunc(sysdate,'MM')-5
            and   dep_name in (:dep_name)
            and   status = 0
            order by event_date desc
        """
    list_approve=[]
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                if subordinate_ou and subordinate_ou is not None:
                    # subordinate_ou = str(session['subordinate_ou'])[1:-1]
                    stmt_new = stmt.replace(':dep_name', subordinate_ou);
                    log.info(f'-------\n\tGET LIST TO APPROVE\n\tUSER: {user.full_name}\n\tSUBORDINATE_OU: {subordinate_ou}\n\tlen: {len(subordinate_ou)}\n\t{len(user.subordinate_ou)} : {user.subordinate_ou}')
                    log.debug(f'-------\n\tGET LIST TO APPROVE. STMT:\n\t{stmt_new}\n-------')
                    cursor.execute(stmt_new)
                elif admin==1:
                    cursor.execute(stmt)
                elif boss==1:
                    log.info(f'-------\n\tGET LIST TO APPROVE\n\tUSER: {user.full_name}\n\tDEP_NAME: {user.dep_name}')
                    log.debug(f'-------\n\tGET LIST TO APPROVE. STMT:\n\t{stmt}\n-------')
                    cursor.execute(stmt, dep_name=user.dep_name)
                rows = cursor.fetchall()
                for row in rows:
                    res = { 'event_date': row[0], 'time_out': row[1], 'time_in': row[2],
                           'employee': row[3], 'post': row[4], 'dep_name': row[5],
                           'cause': row[6], 'head': row[7], 'status': row[8], 'id': row[9]
                           }
                    list_approve.append(res)
            finally:
                log.debug(f'LIST APPROVE. {list_approve}')
    return list_approve


def get_secure_list_to_approve():
    list_approve = []
    stmt = """
        select event_date, time_out, time_in, employee, post, dep_name, cause, head, status , id
        from register r
        where trunc(event_date,'MM') = trunc(sysdate,'MM')
        and   status = 3
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
                           'cause': row[6], 'head': row[7], 'status': row[8], 'id': row[9]
                           }
                    list_approve.append(res)
            finally:
                log.debug(f'SECURE LIST APPROVE. {list_approve}')
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
                log.debug(f'DEL TIME_OFF. username: {employee}, id_reg: {id_reg}')


def fact_time_off(id_reg: int, employee: str):
    stmt = """
        begin reg.fact_time_off(:id_reg); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, id_reg=id_reg)
            finally:
                log.debug(f'FACT TIME_OFF. username: {employee}, id_reg: {id_reg}')


def approve_time_off(id_reg: int, boss: str):
    stmt = """
        begin reg.approve_time_off(:id_reg, :boss); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, id_reg=id_reg, boss=boss)
            finally:
                log.debug(f'DEL TIME_OFF. boss: {boss}, id_reg: {id_reg}')


def refuse_time_off(id_reg: int, boss: str):
    stmt = """
        begin reg.refuse_time_off(:id_reg, :boss); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, id_reg=id_reg, boss=boss)
            finally:
                log.debug(f'REFUSE TIME_OFF. boss: {boss}, id_reg: {id_reg}')


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
                log.debug(f'LIST HEAD. {list_head}')
    return list_head


def add_head(head_name: str):
    stmt = """
        begin reg.add_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.debug(f'ADD HEAD. {head_name}')

    
def del_head(head_name: str):
    stmt = """
        begin reg.del_head(:head_name); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, head_name=head_name)
            finally:
                log.debug(f'DEL HEAD. {head_name}')


def add_message(employee: str, dep_name: str,  mess: str):
    stmt = """
        begin reg.new_message(:employee, :dep_name, :message); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, employee=employee, dep_name=dep_name, message=mess)
            finally:
                log.debug(f'ADD MESSAGE. employee: {employee}, dep_name: {dep_name}, message: {mess}')


def use_file_statistic(user_name, dep_name, file_name, file_path):
    stmt = """
        begin reg.use_file_statistic(:user_name, :dep_name, :file_name, :file_path); end;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, user_name=user_name, dep_name=dep_name, file_name=file_name, file_path=file_path)
            finally:
                log.debug(f'ADD USE_FILE_STATISTIC. employee: {user_name}, dep_name: {dep_name}, file_name: {file_name}')


def get_all_message():
    list_message = []
    stmt = """
        select id_mess, mess_date, author, dep_name, message 
        from messages 
        where mess_date > sysdate-8
        order by mess_date desc
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                rows = cursor.fetchall()
                for row in rows:
                    split_name = row[2].split(' ')
                    short_name = f'{split_name[1][0]}. {split_name[0]}'
                    short_date = str(row[1])[0:16]
                    
                    res = { 'id_mess': row[0], 'mess_date': short_date, 'author': short_name, 'dep_name': row[3], 'message': row[4]}
                    list_message.append(res)
            finally:
                log.debug(f'LIST MESSAGE. {list_message}')
    return list_message


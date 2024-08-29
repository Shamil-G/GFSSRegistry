# from concurrent.futures.thread import BrokenThreadPool
# from gc import enable
# from socket import close
from gfss_parameter import LD_LIBRARY_PATH
from util.logger import log
from util.ip_addr import ip_addr 
import oracledb
import configparser

config = configparser.ConfigParser()
config.read('db_config.ini')

ora_config = config['db_60']

db_user=ora_config['db_user']
db_password=ora_config['db_password']
db_dsn=ora_config['db_dsn']

db_params = config['db_params']

db_debug_level = db_params['debug_level']
db_expire_time = db_params['expire_time']  # количество минут между отправкой keepalive
db_timeout = db_params['timeout']     # В секундах. Время простоя, после которого курсор освобождается
db_wait_timeout = db_params['wait_timeout']  # Время (в миллисекундах) ожидания доступного сеанса в пуле, перед тем как выдать ошибку
db_max_lifetime_session = db_params['max_lifetime_session']  # Время в секундах, в течении которого может существоват сеанс
db_retry_count = db_params['retry_count']
db_retry_delay = db_params['retry_delay']
db_pool_min = db_params['pool_min']
db_pool_max = db_params['pool_max']
db_pool_inc = db_params['pool_inc']


def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_TERRITORY = 'CIS'")
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
    log.info("--------------> Executed: ALTER SESSION SET NLS_TERRITORY = 'CIS'")
    cursor.close()


log.info(f'\n---------------------- START connect --------------------------'
         f'\n\tdb_user: {db_user}, db_pasword: {db_password},'
         f'\n\tdb_dsn: {db_dsn}'
         f'\n\ttimeout: {db_timeout}, wait_timeout: {db_wait_timeout}, expire_time: {db_expire_time}' 
         f'\n\tmax_lifetime_session: {db_max_lifetime_session}, '
         f'\n\tmin: {db_pool_min}, max: {db_pool_max}, increment: {db_pool_inc}, '
         f'\n------------------------   connect   --------------------------\n'
         )

# Для работы "толстого клиента", сначала выполняется init_oracle_client
# Для работы с версией БД ЦРТР требуется толстый клиент
oracledb.init_oracle_client(lib_dir=LD_LIBRARY_PATH)

_pool = oracledb.create_pool(user=db_user, 
                             password=db_password, 
                             dsn=db_dsn,
                             timeout=db_timeout, 
                             wait_timeout=db_wait_timeout,
                             max_lifetime_session=db_max_lifetime_session,
                             min=db_pool_min, max=db_pool_max, 
                             increment=db_pool_inc,
                             expire_time=db_expire_time,
                             session_callback=init_session)

log.info(f'Пул соединенй БД Oracle создан. Timeout: {_pool.timeout}, wait_timeout: {_pool.wait_timeout}, '
            f'max_lifetime_session: {_pool.max_lifetime_session}, min: {db_pool_min}, max: {db_pool_max}')


def get_connection():
    global _pool
    return _pool.acquire()


def close_connection(connection):
    global _pool

    if db_debug_level > 2:
        log.debug("Освобождаем соединение...")
    _pool.release(connection)


def select(stmt):
    results = []
    mistake = 0
    err_mess = ''
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt)
                recs = cursor.fetchall()
                for rec in recs:
                    results.append(rec)
            except oracledb.DatabaseError as e:
                error, = e.args
                mistake = 1
                err_mess = f"Oracle error: {error.code} : {error.message}"
                log.error(f"ERROR with ------select------>\nmess: {err_mess}")
            finally:
                return mistake, results, err_mess


def select_one(stmt, args):
    mistake = 0
    err_mess = ''
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, args)
                rec = cursor.fetchone()
            except oracledb.DatabaseError as e:
                error, = e.args
                mistake = 1
                rec = ''
                err_mess = f"Oracle error: {error.code} : {error.message}"
                log.error(f"ERROR ------select------>\n{stmt}\nARGS: {args}\n{err_mess}")
            finally:
                return mistake, rec, err_mess


def plsql_execute(cursor, f_name, cmd, args):
    try:
        cursor.execute(cmd, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        log.error(f"ERROR ------execute------> FNAME:{f_name}\nIP_Addr: {ip_addr()}, args: {args}\nerror: {error.code} : {error.message}")


def plsql_proc(cursor, f_name, proc_name, args):
    try:
        cursor.callproc(proc_name, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        log.error(f"ERROR -----plsql-proc-----> FNAME: {f_name}\nARGS: {args}\nerror: {error.code} : {error.message}")


def plsql_proc_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            plsql_proc(cursor, f_name, proc_name, args)


def plsql_func(cursor, f_name, func_name, args):
    ret = ''
    try:
        ret = cursor.callfunc(func_name, args)
    except oracledb.DatabaseError as e:
        error, = e.args
        log.error(f"ERROR -----plsql-func-----> FNAME: {f_name}\nargs: {args}\nerror: {error.code} : {error.message}")
    finally:
        return ret


def plsql_func_s(f_name, proc_name, args):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            return plsql_func(cursor, f_name, proc_name, args)


if __name__ == "__main__":
    log.debug("Тестируем CONNECT блок!")
    con = get_connection()
    log.debug("Версия: " + con.version)
    val = "Hello from main"
    con.close()
    _pool.close()
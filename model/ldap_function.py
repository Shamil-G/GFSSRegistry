from datetime import date
from ldap3 import Server, Connection, SUBTREE
from flask import session
from app_config import ldap_admins, ldap_server, ldap_user, ldap_password, ldap_ignore_ou, ldap_boss
from util.ip_addr import ip_addr
from util.logger import log


def find_value(src_string:str, key:str):
    elements = src_string.split(',')
    for element in elements:
        key_field, value = element.split('=')
        if key_field==key:
            return value

def sortElementBD(element:dict):
    sortElement=''
    if 'birth_date' in element:
        sortElement = element['birth_date'][5:]
    log.debug(f'element: {element}, sortelement: {sortElement}')
    return sortElement

def get_connect(username:str, password:str):
    try:
        server = Server(ldap_server)
        log.info(f'CONNECTED to SERVER {ldap_server} SUCCESS')    
        conn = Connection(server, user=username, password=password, auto_bind=True)
        log.info(f'SUCCESS CONNECTED as user: {username}')    
    except:
        log.error(f'MISTAKE connect as user: {username}, password: {password}')    
        return ''
    return conn

def get_list_birthdate():
    conn_src = get_connect(ldap_user, ldap_password)

    if not conn_src:
        return 0,'',''
    
    next_month=''
    curr_year = str(date.today())[2:4]
    curr_centure = str(date.today())[:2]
    curr_month = str(date.today())[5:7]
    curr_month_int = int(curr_month)
    curr_day = str(date.today())[8:10]
    curr_day_int = int(str(date.today())[8:10])
    if curr_day_int<25:
        log.debug(f'GET_LIST_BIRTHDATE. curr_centure: {curr_centure}, curr_year: {curr_year}, curr_month: {curr_month}, curr_day: {curr_day}')
        src_filter = f'(&(objectclass=person)(| (telephoneNumber=*{curr_month}*) ))' 
    else:
        next_month_int = curr_month_int+1
        if next_month_int>12:
            next_month_int=1
        next_month = str(next_month_int).zfill(2)
        log.debug(f'GET_LIST_BIRTHDATE. curr_centure: {curr_centure}, curr_year: {curr_year}, curr_month: {curr_month}, next_month: {next_month}, curr_day: {curr_day}')
        src_filter = f'(&(objectclass=person)(| (telephoneNumber=*{curr_month}*) (telephoneNumber=*{next_month}*) ))' 
        conn_src.search(search_base='dc=gfss,dc=kz', 
                # search_filter=f'(&(objectclass=person)(cn=*))', 
                search_filter=src_filter, 
                attributes=['distinguishedName', 'userPrincipalName', 'cn', 'sAMAccountName', 'description', 'memberof', 'telephoneNumber', '*'],
                # attributes=['distinguishedName', 'userPrincipalName', 'cn', 'displayName', 'description', 'memberof', 'telephoneNumber'],
                search_scope=SUBTREE,
                paged_size=250)
    users = conn_src.entries
    # Connection closed
    
    if len(users)==0:
        log.debug(f'CONNECT_LDAP. FOUND USERS: {len(users)}\n{users}\n--------------------------------------------')
        return 0,'',''

    dn=''
    result_list=[]
    for user in users:
        iin = str(user['telephoneNumber'])
        log.debug(f'-------------\nIIN:\n{iin}\n-------------')
        
        if (iin[2:4] == curr_month and int(iin[4:6])>=curr_day_int and int(iin[4:6])<curr_day_int+10) or (iin[2:4] == next_month and int(iin[4:6])<10):
            dn = str(user['distinguishedName'])
            ou = find_value(dn, 'OU')
            bd_year_int = int(iin[:2])
            if bd_year_int > int(curr_year):
                birth_date = f'{int(curr_centure)-1}{iin[:2]}.{iin[2:4]}.{iin[4:6]}'
            else:
                birth_date = f'{int(curr_centure)}{iin[:2]}.{iin[2:4]}.{iin[4:6]}'
            result_user = { 
                            'birth_date': birth_date,
                            'employee': str(user['displayName']),
                            'post': str(user['description'])
                            }
            log.debug(f'\nDN: {dn}\n-----------------------')
    
            conn_src.search(search_base=f'OU={ou},dc=gfss,dc=kz', 
                        search_filter=f'(objectClass=OrganizationalUnit)', 
                        # attributes=['name', 'description', '*'],
                        attributes=['name', 'description'],
                        search_scope=SUBTREE,
                        paged_size=1)
            orgs = conn_src.entries

            log.debug(f'Found organizations: {orgs}')
            for org in orgs:
                log.debug(f'---\nORG_UNIT: {ou}, dep_name: {str(org['description'])}\n---')
            result_user['dep_name'] = str(orgs[0]['description'])
            result_list.append(result_user)
    result_list.sort(key=sortElementBD)

    conn_src.unbind()

    log.info(f'GET_LIST_BIRTHDATE. SUCCESS. {result_list}')
    return result_list

# import locale
from datetime import date, datetime
from ldap3 import Server, Connection, SUBTREE
from flask import session
from app_config import ldap_server, ldap_user, ldap_password, ldap_ignore_ou, ldap_ignore_ou # ldap_admins, , ldap_boss
# from util.ip_addr import ip_addr
from util.logger import log


def find_value(src_string:str, key:str):
    elements = src_string.split(',')
    for element in elements:
        key_field, value = element.split('=')
        if key_field==key:
            return value

def sortElementBD(element:dict):
    sortElement=''
    if 'birth_date_sort' in element:
        sortElement = element['birth_date_sort'][0:]
    return sortElement

def get_search_dn(src:str):
    index = src.find('OU')
    if index>=0:
        res = src[index:]
    else:
        res = ''
    return res

def get_connect_ldap(username:str, password:str):
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
    conn_src = get_connect_ldap(ldap_user, ldap_password)

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
    
    log.debug(f"-------USERS: \n\t{users}\n-------")
    if len(users)==0:
        log.info(f'CONNECT_LDAP. FOUND USERS: {len(users)}\n{users}\n--------------------------------------------')
        return 0,'',''

    dn=''
    result_list=[]
    for user in users:
        iin = str(user['telephoneNumber'])
        dn = str(user['distinguishedName'])
        ou = find_value(dn, 'OU')
        if ou in ldap_ignore_ou:
            log.debug(f'UVOLEN! {user}')
            continue
        log.debug(f'-------------\nIIN:\n{iin}\n-------------')
        
        if (iin[2:4] == curr_month and int(iin[4:6])>=curr_day_int and int(iin[4:6])<curr_day_int+10) or (iin[2:4] == next_month and int(iin[4:6])<10):
            # cur_locale = locale.getlocale()
            # locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
            bd_date = datetime.strptime(iin[:6], '%y%m%d')
            bd_month = int(iin[2:4])
            if int(curr_month) > bd_month:  # Ситуация в декабре-январе когда 12>1
                birth_date_sort = f'{int(iin[2:4])+1}.{iin[4:6]}'
            else:
                birth_date_sort = f'{iin[2:4]}.{iin[4:6]}'
            birth_date = bd_date.strftime('%d, %B')
            result_user = { 
                            'birth_date': birth_date,
                            'birth_date_sort': birth_date_sort,
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
                log.debug(f'\tORG_UNIT: {ou}, DEP_NAME: {str(org['description'])}\n---')
            result_user['dep_name'] = str(orgs[0]['description'])
            result_list.append(result_user)
    result_list.sort(key=sortElementBD)

    conn_src.unbind()

    log.debug(f'GET_LIST_BIRTHDATE. SUCCESS. {result_list}')
    return result_list


def get_subordinate(conn_ldap, search_dn: str):
    if not conn_ldap:
        log.info(f'MISTAKE GET SUBORDINATE! CONN_USR not OPEN')
        return

    conn_ldap.search(search_base=f'{search_dn}',
                search_filter=f'(objectClass=OrganizationalUnit)', 
                attributes=['name', 'description'],
                search_scope=SUBTREE,
                paged_size=10)

    orgs = conn_ldap.entries    

    log.info(f'GET SUBORDINATE. SEARCH_DN: {search_dn}')
        
    v_int = 0
    subordinate_ou = []
    self_org_name = ''
    self_dep_name = ''
    if 'subordinate_ou' in session:
        session.pop('subordinate_ou')
    if 'dep_name' in session:
        session.pop('dep_name')

    for org in orgs:
        org_name = org['name'].value
        if org_name not in ldap_ignore_ou and org_name.find('COMP') == -1:
            dep_name = org['description'].value
            log.debug(f'+++\nGET SUBORDINATE\n\tORG_NAME: {org_name}\n\tDEP_NAME: {dep_name}\n+++')
            v_int = v_int+1
            if v_int == 1 and org_name and dep_name:
                self_org_name = org_name
                self_dep_name = dep_name
                session['dep_name'] = self_dep_name
            elif dep_name:
                subordinate_ou.append(dep_name) 
    if len(subordinate_ou) > 0:
        session['subordinate_ou'] = subordinate_ou
        log.info(f'-----\n\tGET SUBORDINATE ORG. {session['subordinate_ou']}\n-----')
    log.info(f'GET SUBORDINATE. SUCCESS. OU: {self_org_name}, DEP_NAME: {self_dep_name}')
    # return orgs


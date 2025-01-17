from ldap3 import Server, Connection, SUBTREE
from flask import  session
# from util.logger import log

ldap_server = 'ldap://192.168.1.3:3268'
ldap_user = 'cn=ldp,ou=admins,dc=gfss,dc=kz'
ldap_password = 'hu89_fart7'
ldap_ignore_ou = ['UVOLEN','OLD','Domain Controllers','Admins','WinUpdate','TMP','pfsense','UpOK',
                  'ATT','BUILTIN','Computers','DEKRET', 'gfss', 'Tempo', 'REG', 'Servers_Reg']

def get_connect(username:str, password:str):
    try:
        server = Server(ldap_server)
        # log.info(f'CONNECTED to SERVER {ldap_server} SUCCESS')    
        conn = Connection(server, user=username, password=password, auto_bind=True)
        # log.info(f'SUCCESS CONNECTED as user: {username}')    
    except:
        # log.error(f'MISTAKE connect as user: {username}, password: {password}')    
        return ''
    return conn


def list_ou():
    conn_src = get_connect(ldap_user, ldap_password)
    conn_src.search(search_base='dc=gfss,dc=kz', 
            search_filter='(objectClass=OrganizationalUnit)', 
            attributes=['description', 'OU'],
            search_scope=SUBTREE,
            paged_size=250)
    list_ou=[]
    # print(f'ORG: {conn_src.entries}')
    for el_ou in conn_src.entries:
        ou=str(el_ou['OU'])
        if ou not in ldap_ignore_ou and not ou.endswith('_COMP'):
            el ={'name': ou, 'dep_name': str(el_ou['description'])}
            list_ou.append(el)
    conn_src.unbind()
    return list_ou


def list_employer(ou):
    conn_emp = get_connect(ldap_user, ldap_password)
    search_base=f"ou={ou},dc=gfss,dc=kz"
    search_filter=f'(&(objectclass=person))'
    conn_emp.search(search_base=search_base, 
            search_filter=search_filter, 
            #attributes=['distinguishedName', 'userPrincipalName', 'cn', 'sAMAccountName', 'description', 'memberof', 'telephoneNumber', '*'],
            attributes=['distinguishedName', 'userPrincipalName', 'cn', 'displayName', 'description', 'memberof', 'telephoneNumber'],
            search_scope=SUBTREE,
            paged_size=250)
    list_emp = conn_emp.entries
    conn_emp.unbind()
    return list_emp


if __name__ == "__main__":
    list_ou = list_ou()
    for el_ou in list_ou:
        print(f"\n----- OU: {el_ou['name']}, dep_name: {el_ou['dep_name']} -----")
        list_emp = list_employer(el_ou['name'])
        # print(f'----- EMP: \t\n{list_emp}\n----- EMP\n')
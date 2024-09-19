from ldap3 import Server, Connection, SUBTREE
from flask import session
from app_config import ldap_admins, ldap_server, ldap_user, ldap_password
from util.ip_addr import ip_addr
from util.logger import log

#from logger import log

#ldap_server = 'ldap://192.168.1.3:3268'

#ldap_user = 'cn=ldp,ou=admins,dc=gfss,dc=kz'
#ldap_password = 'hu89_fart7'


def find_value(src_string:str, key:str):
    elements = src_string.split(',')
    for element in elements:
        key_field, value = element.split('=')
        if key_field==key:
            return value

def get_connect(username:str, password:str):
    try:
        server = Server(ldap_server)
        log.error(f'CONNECTED to SERVER {ldap_server} SUCCESS')    
        conn = Connection(server, user=username, password=password, auto_bind=True)
        log.error(f'SUCCESS CONNECTED as user: {username}')    
    except:
        log.error(f'MISTAKE connect as user: {username}, password: {password}')    
        return ''
    return conn

def connect_ldap(username:str, password:str):
    success = 1
    conn_src = get_connect(ldap_user, ldap_password)

    if not conn_src:
        return 0,'',''
    
    log.debug(f'NOW search username: {username}')
    conn_src.search(search_base='dc=gfss,dc=kz', 
                search_filter=f'(&(objectclass=person)(cn={username}*))', 
                # attributes=['distinguishedName', 'userPrincipalName', 'cn', 'sAMAccountName', 'description', 'memberof', '*'],
                attributes=['distinguishedName', 'userPrincipalName', 'cn', 'description', 'memberof'],
                search_scope=SUBTREE,
                paged_size=5)
    users = conn_src.entries
    conn_src.unbind()
    # Connection closed
    
    if len(users)==0:
        log.debug(f'CONNECT_LDAP. FOUND USERS: {len(users)}\n{users}\n--------------------------------------------')
        return 0,'',''

    log.debug(f'\nUSERS:\n{users}\n-----------------------')
    dn=''
    principalName=''
    full_name=''
    ou=''
    for user in users:
        dn = str(user['distinguishedName'])
        principalName = str(user['userPrincipalName'])
        full_name = str(user['CN'])
        session['post'] = str(user['description'])
        
        # acc_name = user['sAMAccountName']
        # members = user['memberOf']
        # for member in members:
        #     ou = find_value(member, 'OU')
        #     if ou:
        #         break
        ou = find_value(dn, 'OU')
             
        conn_usr = get_connect(principalName, password)
        if conn_usr:
            break

    if not conn_usr:
        log.info(f'USER NOT FOUND user: {principalName} : {password}.\nMISTAKE !!!\n---------------------------')
        return 0,'',''
       
    log.debug(f'\nDN: {dn}\n-----------------------')
    log.debug(f'SUCCESS CONNECTED as user {principalName}. post: {session['post']}\nfull_name: {full_name},\nOU: {ou}\nNOW will be search ORGANIZATION UNIT')
    
    conn_usr.search(search_base=f'OU={ou},dc=gfss,dc=kz', 
                search_filter=f'(objectClass=OrganizationalUnit)', 
                # attributes=['name', 'description', '*'],
                attributes=['name', 'description'],
                search_scope=SUBTREE,
                paged_size=5)

    orgs = conn_usr.entries    
    conn_usr.unbind()
        
    log.debug(f'Found organizations: {orgs}')
    for org in orgs:
        org_name = org['name']
        session['dep_name'] = str(org['description'])
        log.debug(f'-------------------------\nORG_UNIT: {ou}, org_name: {org_name}, org_descr: {session['dep_name']}\n--------------------------------')

    log.info(f'CONNECT LDAP. SUCCESS. {principalName} : {full_name} : {session['dep_name']}')
    return success, principalName, full_name

        
class LDAP_User:
    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        session['admin']=0
        if 'password' in session:
            self.password = session['password']
        if src_user:
            success, login_name, full_name = connect_ldap(src_user, self.password)
            log.debug(f'LM. success: {success}, html_user: {src_user}, password: {self.password}, full_name: {full_name}, login_name: {login_name}')
            if success > 0:
                log.info(f'LDAP_User. {full_name} : {login_name}')
                self.username = login_name
                session['username'] = login_name
                
                self.full_name = full_name
                session['full_name'] = full_name 
                # log.debug(f'ldap_admins: {ldap_admins}')
                if session['full_name'] in ldap_admins:
                    session['admin']=1
                
                self.ip_addr = ip
                log.info(f"LM. SUCCESS. USERNAME: {self.username}, ip_addr: {self.ip_addr}\n\tFIO: {self.full_name}\n\tadmin: {session['admin']}")
                return self
        log.info(f"LM. FAIL. USERNAME: {src_user}, ip_addr: {ip}, password: {session['password']}, admin: {session['admin']}")
        return None

    def have_role(self, role_name):
        if hasattr(self, 'username'):
            return role_name in self.roles

    def is_authenticated(self):
        if not hasattr(self, 'username'):
            return False
        else:
            return True

    def is_active(self):
        if hasattr(self, 'username'):
            return True
        else:
            return False

    def is_anonymous(self):
        if not self.username:
            return True
        else:
            return False

    def get_id(self):
        log.debug(f'LDAP_User. GET_ID. self.src_user: {self.src_user}, self.username: {self.username}')
        if hasattr(self, 'src_user'):
            return self.src_user
        else: 
            return None


if __name__ == "__main__":
    #'bind_dn'       => 'cn=ldp,ou=admins,dc=gfss,dc=kz',
    #'bind_pass'     => 'hu89_fart7',    
    #get_users('Гусейнов_Ш@GFSS', 'Strptz256')
    connect_ldap('Гусейнов', 'Strptz256')
    #get_users('Гусейнов_Ш', 'Strptz256')
    #get_users('s.gusseynov@GFSS', 'Strptz256')






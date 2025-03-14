from ldap3 import Server, Connection, SUBTREE
from flask import session
from app_config import ldap_admins, approve_admins, ldap_server, ldap_user, ldap_password, ldap_ignore_ou, ldap_boss
from util.ip_addr import ip_addr
from util.logger import log
from model.ldap_function import get_subordinate, get_search_dn, get_connect_ldap, find_value


def connect_ldap(username:str, password:str):
    success = 1
    conn_src = get_connect_ldap(ldap_user, ldap_password)

    if not conn_src:
        return 0,'',''
    
    log.debug(f'NOW search username: {username}')
    conn_src.search(search_base='dc=gfss,dc=kz', 
                # search_filter=f'(&(objectclass=person)(cn=*))', 
                search_filter=f'(&(objectclass=person)(| (cn={username}*) (displayname={username}*) (telephoneNumber={username}*) ))', 
                attributes=['distinguishedName', 'userPrincipalName', 'cn', 'sAMAccountName', 'description', 'memberof', 'telephoneNumber', 'employeeNumber', '*'],
                # attributes=['distinguishedName', 'userPrincipalName', 'cn', 'displayName', 'description', 'memberof', 'telephoneNumber'],
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
    search_dn=''
    conn_usr=''
    employeeNumber=''
    for user in users:
        dn = user['distinguishedName'].value
        search_dn = get_search_dn(dn)
        # search_dn = get_ou(dn)
        principalName = user['userPrincipalName'].value

        ou = find_value(dn, 'OU')
        
        if ou not in ldap_ignore_ou:
            conn_usr = get_connect_ldap(principalName, password)
            log.debug(f'GET CONNECT. OU: {ou}, principalName: {principalName}')
            if conn_usr:
                if 'employeeNumber' in user:
                    employeeNumber = user['employeeNumber'].value
                if 'displayName' in user:
                    full_name = user['displayName'].value
                if 'description' in user:
                    session['post'] = user['description'].value
                    if session['post'] in ldap_boss:
                        session['boss']=1
                    elif 'boss' in session:
                        session.pop('boss')
                break

    if not conn_usr:
        log.info(f'USER NOT FOUND user: {principalName} : {password}.\nMISTAKE !!!\n---------------------------')
        return 0,'',''
       
    log.debug(f'-----------------------\nSEARCH_DN: {search_dn}\n-----------------------')
    log.debug(f'SUCCESS CONNECTED as user {principalName}. \n\tPOST: {session['post']}'
              f'\n\tfull_name: {full_name}\n\temployeeNumber: {employeeNumber}'
              '\nNOW will be search ORGANIZATION UNIT ...\n-----------------------')
    
    get_subordinate(conn_usr, search_dn)
    conn_usr.unbind()
        
    log.info(f'CONNECT LDAP. SUCCESS. {principalName} : {full_name}\n\tPOST: {session['post']}\n\tDEP_NAME: {session['dep_name']}')
    return success, principalName, full_name

        
class LDAP_User:
    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        self.post=''
        self.dep_name=''
        session['admin']=0
        session['approve_admin']=0
        if 'password' in session:
            self.password = session['password']
        if src_user:
            success, login_name, full_name = connect_ldap(src_user, self.password)
            if success > 0:
                log.debug(f'LM LDAP. success: {success}, login_user: {src_user}, password: {self.password}, full_name: {full_name}, login_name: {login_name}')
                self.username = login_name
                session['username'] = login_name

                if 'post' in session:
                    self.post = session['post']
                if 'dep_name' in session:
                    self.dep_name = session['dep_name']
                
                self.full_name = full_name
                session['full_name'] = full_name 
                # log.debug(f'ldap_admins: {ldap_admins}')
                if session['full_name'] in ldap_admins:
                    session['admin']=1
                if session['full_name'] in approve_admins:
                    session['approve_admin']=1
                
                self.ip_addr = ip
                log.info(f"LM LDAP. SUCCESS. USERNAME: {self.username}, ip_addr: {self.ip_addr}\n\tFIO: {self.full_name}\n\tadmin: {session['admin']}, approve_admin: {session['approve_admin']}")
                return self
            log.info(f"LM LDAP. FAIL. USERNAME: {src_user}, ip_addr: {ip}, password: {session['password']}")
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
    connect_ldap('Гусейнов', '123')

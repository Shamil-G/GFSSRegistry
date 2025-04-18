from flask import session
from util.ip_addr import ip_addr
from util.logger import log
from app_config import approve_admins, boss

     
class SSO_User:
    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        self.post=''
        self.depname=''
        session['admin']=0
        session['approve_admin']=0
        if 'password' in session:
            self.password = session['password']
        if src_user and 'login_name' in src_user:
            log.debug(f'SSO_USER. src_user: {src_user}')

            if 'principalName' in src_user:
                self.principalName= src_user['principalName']

            if 'fio' in src_user:
                self.full_name = src_user['fio']
            else:
                self.full_name = 'unknown'
            session['full_name'] = self.full_name

            if session['full_name'] in approve_admins:
                self.approve_admin = 1
                session['approve_admin']=1

            if 'login_name' in src_user:
                self.username = src_user['login_name']
            else:
                self.username = 'unknown'
            session['username'] = self.username 

            if 'post' in src_user:
                self.post = src_user['post']
            else:
                self.post = 'unknown'
            session['post']=self.post

            if 'dep_name' in src_user:
                self.dep_name = src_user['dep_name']
            else:
                self.dep_name = 'unknown'
            session['dep_name']=self.dep_name

            if 'subordinate_ou' in src_user:
                self.subordinate_ou = src_user['subordinate_ou']

            self.roles=[]
            # Здесь безопасники, кто может утверждать независимо от должности
            if self.full_name in approve_admins:
                self.roles.append('admin')
            # Здесь руководители подразделений
            if self.post in boss:
                self.roles.append('boss')
                
            self.ip_addr = ip
            log.info(f"SSO USER. SUCCESS. USERNAME: {self.username}, ip_addr: {self.ip_addr}\n\tFIO: {self.full_name}/{self.roles}")
            return self
        log.debug(f"SSO USER. FAIL. USERNAME: {src_user}, ip_addr: {ip}")
        return None

    def have_role(self, role_name):
        if hasattr(self, 'username'):
            return role_name in self.roles

    def is_authenticated(self):
        if hasattr(self, 'username'):
            return True
        else:
            return False

    def is_active(self):
        if hasattr(self, 'username'):
            return True
        else:
            return False

    def is_anonymous(self):
        if hasattr(self, 'username'):
            return False
        else:
            return True

    def get_id(self):
        if hasattr(self, 'principalName'):
            return self.src_user
        else: 
            return None


if __name__ == "__main__":
    #'bind_dn'       => 'cn=ldp,ou=admins,dc=gfss,dc=kz',
    #'bind_pass'     => 'hu89_fart7',    
    #connect_ldap('Гусейнов', '123')
    log.debug(f'__main__ function')

from gfss_parameter import BASE

styles = 'issatay'

debug_level = 2
host = 'localhost'
port=9000
src_lang = 'file'
language = 'ru'
LOG_PATH = f"{BASE}/logs"
REPORT_PATH = f"{BASE}/spool"

URL_LOGIN = 'http://192.168.1.34:8000'

#ldap_admins = ['Алибаева Мадина Жасулановна']
ldap_admins = ['Гусейнов Шамиль Аладдинович', 'Алибаева Мадина Жасулановна']
ldap_server = 'ldap://192.168.1.3:3268'
ldap_user = 'cn=ldp,ou=admins,dc=gfss,dc=kz'
ldap_password = 'hu89_fart7'
ldap_ignore_ou = ['UVOLEN',]
#ldap_boss = ['Директор', 'Руководитель','Главный разработчик']
ldap_boss = ['Директор', 'Руководитель']
from gfss_parameter import BASE

styles = ['color','dark']

host = 'localhost'
port=9000
src_lang = 'file'
language = 'ru'
LOG_PATH = f"{BASE}/logs"
REPORT_PATH = f"{BASE}/spool"

URL_LOGIN = 'http://192.168.1.34:8000'

#ldap_admins = ['Алибаева Мадина Жасулановна', 'Маликов Айдар Амангельдыевич']
boss = ['Директор', 'Руководитель','И.о. директора', 'Заместитель директора']
# boss = ['Директор', 'Руководитель','Главный разработчик','И.о. директора']
approve_admins = ['Гусейнов Шамиль Аладдинович', 'Алибаева Мадина Жасулановна', 'Маликов Айдар Амангельдыевич']
# approve_admins = ['Алибаева Мадина Жасулановна', 'Маликов Айдар Амангельдыевич']

ldap_server = 'ldap://192.168.1.3:3268'
sso_server = 'http://192.168.1.34:8825'
ldap_user = 'cn=ldp,ou=admins,dc=gfss,dc=kz'
ldap_password = 'hu89_fart7'
ldap_ignore_ou = ['UVOLEN','OLD','Domain Controllers','Admins','WinUpdate','TMP','pfsense','UpOK',
                  'ATT','BUILTIN','Computers','DEKRET', 'gfss', 'Tempo', 'REG', 'Servers_Reg']
#ldap_boss = ['Директор', 'Руководитель']
import os

app_name = "GFSSRegistry"
public_name = "Регистрация времени отсутствия"
http_ip_context='HTTP_X_FORWARDED_FOR'
#http_ip_context='HTTP_X_REAL_IP'

# 
app_home="C:/Projects"
platform='!unix'
ORACLE_HOME=r'C:\instantclient_21_3'
LD_LIBRARY_PATH=f'{ORACLE_HOME}'

if "HOME" in os.environ:
    app_home=os.environ["HOME"]
    platform='unix'

if "ORACLE_HOME" in os.environ:
    ORACLE_HOME=f'{os.environ["ORACLE_HOME"]}'
    LD_LIBRARY_PATH=f'{ORACLE_HOME}/lib'

BASE=f'{app_home}/{app_name}'
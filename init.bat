rem python -m venv venv
rem . /home/registry/venv/bin/activate

call C:\Projects\GFSSRegistry\venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip3 install oracledb
pip3 install flask
pip3 install flask_login
pip3 install redis
pip3 install flask_session
pip3 install openpyxl
pip3 install requests
pip3 install gevent
pip3 install gunicorn
pip3 install ldap3
pip3 install xlsxwriter
python main_app.py

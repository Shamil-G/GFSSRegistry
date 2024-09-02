#python3 -m venv venv
. $VENV_HOME/bin/activate

pip3 install --upgrade pip
pip3 install oracledb
pip3 install flask
pip3 install flask_login
pip3 install redis
pip3 install flask_session
pip3 install openpyxl
pip3 install requests
pip3 install gevent
pip3 install gunicorn
python3 main_app.py

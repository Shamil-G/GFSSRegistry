set VIRTUAL_ENV=C:/Projects/GFSSRegistry/venv
rem python -m venv venv
rem call %VIRTUAL_ENV%/bin/activate
call %VIRTUAL_ENV%/Scripts/activate.bat

python -m pip install --upgrade pip
rem pip install oracledb
rempip install flask
rempip install flask_login
rem pip install redis
rem pip install flask_session
rem pip install openpyxl
rem pip install requests
rem pip freeze > requirements.txt
python main_app.py

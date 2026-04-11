from flask import render_template, request, redirect, flash, url_for, g, session
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from sso.sso_login import SSO_User
from main_app import app, log
from app_config import sso_server
from util.ip_addr import ip_addr
from os import environ
import requests 
import json

login_manager = LoginManager(app)
login_manager.login_view = 'login_page_get'
login_manager.login_message = "Необходимо зарегистрироваться в системе"
login_manager.login_message_category = "warning"

log.info("user_login_sso стартовал...")

# 11.04.2026
# @login_manager.user_loader
# def loader_user(id_user):
#     # return User().get_user_by_name(id_user)
#     return SSO_User().get_user_by_name(id_user)

def fetch_user_from_sso(endpoint: str, req_json: dict) -> SSO_User | None:
    resp = requests.post(url=f'{sso_server}/{endpoint}', json=req_json)
    if resp.status_code == 200:
        resp_json = resp.json()
        if resp_json.get('status') == 200 and 'user' in resp_json:
            return SSO_User().get_user_by_name(resp_json['user'])
    return None

@login_manager.user_loader
def loader_user(id_user):
    return fetch_user_from_sso("check", {"ip_addr": ip_addr(), "login_name": id_user})


def try_auto_login():
    ip = ip_addr()
    req_json = {"ip_addr": ip}
    if ip == "127.0.0.1" and "username" in session:
        req_json["login_name"] = session["username"]
    user = fetch_user_from_sso("check", req_json)
    if user:
        login_user(user)
        log.info(f"TRY AUTO LOGIN. USER {ip} SUCCESS Registered")
        return True
    log.info(f"TRY AUTO LOGIN. USER {ip} FAIL Registered")
    return False


@app.after_request
def redirect_to_signing(response):
    if response.status_code == 401:
        return redirect(url_for('view_root') + '?next=' + request.url)
    return response
    

@app.before_request
def before_request():
    g.user = current_user


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    log.info(f"LM. LOGOUT. USERNAME: {session['username']}, ip_addr: {ip_addr()}")
    username = session['username']

    req_json = {'ip_addr': f'{ip_addr()}', 'login_name': username}

    logout_user()
    if 'username' in session:
        session.pop('username')
    if 'password' in session:
        session.pop('password')
    if 'info' in session:
        session.pop('info')
    if 'list_bd' in session:
        session.pop('list_bd')
    if '_flashes' in session:
        session['_flashes'].clear()


    resp = requests.post(url=f'{sso_server}/close', json=req_json)

    if resp.status_code != 200:
        log.info(f'----------------\n\tОшибка {resp.status_code} соединения {username} с сервером SSO\n----------------')
        return redirect(url_for('view_root'))

    resp_json = resp.json()

    if 'status' in resp_json and resp_json['status'] !=200:
        log.info(f'----------------\n\tОшибка закрытия сессии. Статус: {resp_json['status']}/{ip_addr()}\n----------------')

    return redirect(url_for('view_root'))


@app.get('/login')
def login_page_get():

    if g.user.is_authenticated:
        return redirect(url_for('view_root'))

    if try_auto_login():
        log.info('LOGIN_PAGE_GET. try_auto_login SUCCESS')
        return redirect(url_for('view_root'))

    # Настройка стилей
    if 'styles' not in session:
        session['styles'] = environ.get("STYLES", "styles")

    # Очистка flash-сообщений
    if '_flashes' in session:
        session['_flashes'].clear()

    return render_template('login.html', info=request.args.get('info'))



@app.post('/login')
def login_page_post():
    req_json = {
        "login_name": request.form.get("username"),
        "password": request.form.get("password"),
        "ip_addr": ip_addr(),
    }
    user = fetch_user_from_sso("login", req_json)

    if not user:
        log.info(f'---\nLOGIN PAGE POST. FAIL: {req_json}\n---')
        return redirect(url_for("login_page_get", info="Ошибка авторизации"))
    login_user(user)
    return redirect(url_for("view_root"))

from typing import List, Any
from flask import render_template, request, redirect, flash, url_for, g, session
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from util.get_i18n import get_i18n_value
from werkzeug.security import check_password_hash, generate_password_hash
from db.connect import get_connection
from main_app import app, log
import app_config as cfg
from model.manage_user import get_user_roles, server_logout, user_info
from gfss_parameter import public_name
from util.ip_addr import ip_addr
import oracledb


login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = "Необходимо зарегистрироваться в системе"
login_manager.login_message_category = "warning"

log.debug("user_login стартовал...")


class User:
    def get_user_by_name(self, username):
        ip = ip_addr()
        if 'password' in session and 'password' in session:
            rl = get_user_roles(session['username'], session['password'], ip)
            if 'roles' in rl and 'id_user' in rl and len(rl) > 0:
                u_info = user_info(session['username'])
                log.info(f'LM. user_info: {u_info}')
                self.username = username
                self.password = session['password']
                self.ip_addr = ip
                self.id_user = rl['id_user']
                self.roles = rl['roles']
                session['dep_name'] = u_info['dep_name']
                session['post'] = u_info['post']
                session['first_name'] = u_info['first_name']
                session['last_name'] = u_info['last_name']
                session['middle_name'] = u_info['middle_name']
                log.info(f"LM. SUCCESS. USERNAME: {self.username}, ip_addr: {self.ip_addr}"
                         f"\n\tdep_name: {session['dep_name']}\n\tpost: {session['post']}\n\tFIO: {session['last_name']} {session['first_name']} {session['middle_name']}")
                return self
        log.info(f"LM. FAIL. USERNAME: {username}, ip_addr: {ip}, password: {session['password']}")
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
        if hasattr(self, 'username'):
            return self.username
        else: 
            return None


@login_manager.user_loader
def loader_user(id_user):
    if cfg.debug_level > 1:
        log.debug(f"LM. Loader ID User: {id_user}")
    return User().get_user_by_name(id_user)


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
    server_logout(g.user.id_user)
    logout_user()
    if 'username' in session:
        session.pop('username')
    if 'password' in session:
        session.pop('password')
    if 'info' in session:
        session.pop('info')
    if '_flashes' in session:
        session['_flashes'].clear()
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if '_flashes' in session:
         session['_flashes'].clear()
    
    if request.method == "POST":
        session['username'] = request.form.get('username')
        session['password'] = request.form.get('password')
        log.debug(f"LOGIN_PAGE. POST. lang: username: {session['username']}, password: {session['password']}, ip_addr: {ip_addr()}")

        user = User().get_user_by_name(session['username'])

        # Если такой username существует и объект user создался, надо проверить пароль и вытащить атрибуты
        if user:
            login_user(user)
            next_page = request.args.get('next')
            if next_page is not None:
                log.info(f'LOGIN_PAGE. SUCCESS AUTHORITY. GOTO NEXT PAGE: {next_page}')
                return redirect(next_page)
            else:
                return redirect(url_for('view_root'))
        else:
            log.error(f'LOGIN_PAGE. FAIL USERNAME. {session['username']}')
        flash("Имя пользователя или пароль неверны")
        log.error(f'LOGIN_PAGE. FAIL AUTHORITY')
    flash('Введите имя и пароль')
    return render_template('login.html')


# @app.context_processor
# def get_current_user():
    # if g.user.id_user:
    # if g.user.is_anonymous:
    #     log.debug('Anonymous current_user!')
    # if g.user.is_authenticated:
    #     log.debug('Authenticated current_user: '+str(g.user.username))
    # return{"current_user": 'admin_user'}
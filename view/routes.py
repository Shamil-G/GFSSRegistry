from gfss_parameter import platform
from app_config import REPORT_PATH, debug_level
from main_app import app, log
from flask import  session, flash, request, render_template, redirect, url_for, send_from_directory, g
from flask_login import  login_required
import os
from datetime import date
from util.get_i18n import get_i18n_value
from model.manage_user import add_time_off, add_head, del_head, get_list_head


list_params = []

empty_response_save = """
<h2>Hello World</h2>
<p>Maybe Must be used POST method with JSON data</p>
"""

empty_call_response = """
<h2>Hello World</h2>
<p>Maybe Must be used POST method with JSON data: DEP, GROUP and CODE parameter</p>
"""

#@app.route('/', methods=['POST', 'GET'])
#def view_index():
#    return empty_response_save, 200, {'Content-Type': 'text/html;charset=utf-8'}


@app.context_processor
def utility_processor():
    log.info(f"CP. {get_i18n_value('APP_NAME')}")
    return dict(res_value=get_i18n_value)


@app.route('/')
@app.route('/home', methods=['POST', 'GET'])
#@login_required
def view_root():
    # owners = get_owner_reports()
    if debug_level > 1 and 'username' in session:
        log.info(f"VIEW_ROOT. USERNAME: {session['username']}")
    return render_template("index.html")


@app.route('/time-off', methods=['GET','POST'])
@login_required
def view_time_off():
    log.info(f'SET TIME_OFF for {session['username']}')
    list_heads = get_list_head()
    if request.method == 'POST':
        date_out = request.form['date_out'].replace('T',' ',1)
        date_in = request.form['date_in'].replace('T',' ',1)
        cause = request.form['cause']
        head_name = request.form['head_name']

        dep_name = session['dep_name']
        post = session['post']

        employee = f"{session['last_name']} {session['first_name'][0]}. {session['middle_name'][0]}."
        if debug_level > 2:
            log.info(f"VIEW_TIME-OFF. date_out: {date_out}, date_in: {date_in}, "
                     f"\n\temployee: {employee}\n\tpost: {post}\n\tdep_name: {dep_name}\n\tcause: {cause}")
        add_time_off(date_out, date_in, employee, post, dep_name, cause, head_name)
    return render_template("time_off.html", list_heads=list_heads)

@app.route('/heads', methods=['GET','POST'])
@login_required
def view_heads():
    log.info(f'VIEW HEADS. username {session['username']}')
    list_heads = get_list_head()
    if request.method == 'POST':
        head_name = request.form['head_name']
                
        if debug_level > 2:
            log.info(f"VIEW_TIME-OFF. head_name: {head_name}\n\list_head: {list_heads}")
        add_head(head_name)
        return redirect(url_for('view_heads'))
    return render_template("heads.html", list_heads=list_heads)

@app.route('/del-head/<string:head_name>', methods=['GET','POST'])
@login_required
def view_del_head(head_name):
    log.info(f'VIEW HEADS. username {session['username']}')
    del_head(head_name)
    return redirect(url_for('view_heads'))


@app.route('/language/<string:lang>')
def set_language(lang):
    log.info(f"Set language. LANG: {lang}, предыдущий язык: {session['language']}")
    session['language'] = lang
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.info(f"Set LANGUAGE. {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/change-passwd', methods=['POST', 'GET'])
def view_change_password():
    log.info(f"CHANGE PASSWORD")
    if '_flashes' in session:
        session['_flashes'].clear()
    if request.method == "POST":
        passwd_1 = request.form['password_1']
        passwd_2 = request.form['password_2']
        if passwd_1 != passwd_2:
            flash('Пароли не совпадают')
        else:
            change_passwd(session['username'], session['password'], passwd_1)
            return redirect(url_for('view_root'))
    return render_template("change_passwd.html")


@app.route('/uploads/<path:full_path>')
def uploaded_file(full_path):
    if platform == 'unix' and not full_path.startswith('/'):
        full_path = f'/{full_path}'
    path, file_name = os.path.split(full_path)
    if full_path.startswith(REPORT_PATH):
        status = check_report(full_path)
        if debug_level > 2:
            log.info(f"UPLOADED_FILE. STATUS: {status} : {type(status)}, PATH: {path}, file_name: {file_name}, REPORT_PATH: {REPORT_PATH}")
        if status == 2:
            log.info(f"UPLOADED_FILE. PATH: {path}, FILE_NAME: {file_name}")
            return send_from_directory(path, file_name)
    else:
        log.info(f"UPLOADED_FILE. FULL_PATH: {full_path}\nsplit_path: {path}\nreprt_path: {REPORT_PATH}")
    return redirect(url_for('view_running_reports'))

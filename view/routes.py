from gfss_parameter import platform
from app_config import REPORT_PATH, debug_level
from main_app import app, log
from flask import  session, flash, request, render_template, redirect, url_for, send_from_directory, g
from flask_login import  login_required
import os
from datetime import date
from util.get_i18n import get_i18n_value
from model.manage_user import add_time_off, add_head, del_head, get_list_head, get_list_time_off
from model.manage_user import get_all_list_time_off, del_time_off, get_list_absent, get_list_to_approve, approve_time_off
from model.rep_all_time_off import do_report
from model.ldap_function import get_list_birthdate


@app.context_processor
def utility_processor():
    log.info(f"CP. {get_i18n_value('APP_NAME')}")
    return dict(res_value=get_i18n_value)


@app.route('/')
@app.route('/home', methods=['POST', 'GET'])
@login_required
def view_root():
    if 'admin' in session and 'username' in session:
        log.debug(f"VIEW_ROOT. USERNAME: {session['username']}, ADMIN: {session['admin']}")
    list_bd = get_list_birthdate()
    return render_template("index.html", list_bd=list_bd)


@app.route('/time-off', methods=['GET','POST'])
@login_required
def view_time_off():
    log.info(f'SET TIME_OFF for {session['username']}')
    # list_heads = get_list_head()
    message = ''
    if request.method == 'POST':
        date_out = request.form['date_out'].replace('T',' ',1)
        date_in = request.form['date_in'].replace('T',' ',1)
        cause = request.form['cause']
        if 'head_name' in request.form:
            head_name = request.form['head_name']
            # if not head_name:
            #     message = 'Не указан руководитель'
        if not date_out:
            message = 'Не указано время ухода'
        if not date_in:
            message = 'Не указано время прихода'
        if not cause:
            message = 'Не указана причина ухода'
        
        if not message:
            dep_name=''
            post=''
            if 'dep_name' in session:
                dep_name = session['dep_name']
            if 'post' in session:
                post = session['post']

            # if 'last_name' in session:
            #     employee = f"{session['last_name']} {session['first_name'][0]}. {session['middle_name'][0]}."
            # else:
            employee = session['full_name']
        
            log.debug(f"VIEW_TIME-OFF. date_out: {date_out}, date_in: {date_in}, "
                        f"\n\temployee: {employee}\n\tpost: {post}\n\tdep_name: {dep_name}\n\tcause: {cause}")
            message = add_time_off(date_out, date_in, employee, post, dep_name, cause)
            return redirect(url_for('view_list_time_off'))            
    if message == 'Success':
        message = 'Регистрация завершена успешно'
    elif message:
        log.error(f'VIEW_TIME_OFF. ERROR: {message}')
    # return render_template("time_off.html", message = message, list_heads=list_heads)
    return render_template("time_off.html", message = message)


@app.route('/list-time-off')
@login_required
def view_list_time_off():
    log.debug(f'VIEW LIST TIME OFF. username {session['full_name']}, admin: {session['admin']}')
    list_time_off = get_list_time_off(session['full_name'])
    return render_template("list_time_off.html", list_time_off=list_time_off)


@app.route('/list-absent')
@login_required
def view_list_absent():
    log.debug(f'VIEW LIST ABSENT. username {session['full_name']}, admin: {session['admin']}')
    list_absent = get_list_absent()
    return render_template("list_absent.html", list_absent=list_absent)


@app.route('/all-list-time-off', methods=['GET','POST'])
@login_required
def view_all_list_time_off():
    log.debug(f'VIEW LIST TIME OFF. username {session['full_name']}, admin: {session['admin']}')
    if 'flt_month' not in session:
        session['flt_month'] = str(date.today())[0:7]
    if request.method == 'POST':
        flt_month = request.form['flt_month']  
        log.info(f' FLT_MONTH: {flt_month} : {type(flt_month)}')
        session['flt_month'] = flt_month
    list_time_off = get_all_list_time_off(f'{session['flt_month']}-01')
    return render_template("list_all_time_off.html", list_time_off=list_time_off, flt_month=session['flt_month'])


@app.route('/list-to-approve', methods=['GET','POST'])
@login_required
def view_list_approve():
    log.debug(f'VIEW LIST APPROVE. username {session['full_name']}, admin: {session['admin']}')
    log.debug(f'VIEW LIST APPROVE. dep_name: {session['dep_name']} : {type(session['dep_name'])}')
    list_approve = get_list_to_approve(session['dep_name'])
    return render_template("list_approve.html", list_approve=list_approve)


@app.route('/approve-time-off/<int:id_reg>', methods=['GET','POST'])
@login_required
def view_approve_time_off(id_reg):
    log.debug(f'VIEW HEADS. username {session['username']}')
    approve_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_approve'))


@app.route('/del-from-list-time-off/<int:id_reg>')
@login_required
def view_del_from_list_time_off(id_reg):
    log.debug(f'VIEW LIST TIME_OFF. username {session['username']}')
    del_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_time_off'))


@app.route('/heads', methods=['GET','POST'])
@login_required
def view_heads():
    log.debug(f'VIEW HEADS. username {session['username']}')
    list_heads = get_list_head()
    if request.method == 'POST':
        head_name = request.form['head_name']
                
        if debug_level > 2:
            log.info(f"VIEW_TIME-OFF. head_name: {head_name}\n\tlist_head: {list_heads}")
        add_head(head_name)
        return redirect(url_for('view_heads'))
    return render_template("heads.html", list_heads=list_heads)


@app.route('/del-head/<string:head_name>', methods=['GET','POST'])
@login_required
def view_del_head(head_name):
    log.debug(f'VIEW HEADS. username {session['username']}')
    del_head(head_name)
    return redirect(url_for('view_heads'))


@app.route('/language/<string:lang>')
def set_language(lang):
    log.debug(f"Set language. LANG: {lang}, предыдущий язык: {session['language']}")
    session['language'] = lang
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set LANGUAGE. {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/uploads')
def uploaded_file():
    file_name = 'rep_all_time_off.xlsx'
    do_report(session['flt_month'], file_name)
    log.debug(f"UPLOADED_FILE. REPORT_PATH: {REPORT_PATH} FILE_NAME: {file_name}")
    return send_from_directory(REPORT_PATH, file_name)
    # return redirect(url_for('view_running_reports'))

from locale import setlocale, LC_ALL
from gfss_parameter import platform
from app_config import REPORT_PATH, styles, sso_server
from main_app import app, log
from flask import  session, flash, request, render_template, redirect, url_for, send_from_directory, g
from flask_login import  login_required, login_user
import os
from datetime import date
from util.get_i18n import get_i18n_value
from model.manage_user import add_head, del_head, get_list_head, get_list_time_off
from model.manage_user import get_all_list_time_off, get_list_absent, get_list_to_approve, get_secure_list_to_approve
from model.manage_user import add_time_off, add_secure_time_off, fact_time_off, del_time_off, get_all_message, add_message
from model.manage_user import approve_time_off, refuse_time_off
from model.rep_all_time_off import do_report
from model.list_bd import get_list_birthdate
from model.ldap_function import get_all_employers
import requests
from os import environ
from sso.sso_login import SSO_User
from util.ip_addr import ip_addr


setlocale(LC_ALL, 'ru_RU.UTF-8')


@app.context_processor
def utility_processor():
    if 'style' not in session:
        session['style']=styles[0]    
        log.info(f'------- CP\n\tSET SESSION STYLE: {session['style']}\n------')
    log.debug(f"CP. {get_i18n_value('APP_NAME')}")
    return dict(res_value=get_i18n_value)


def try_auto_login():
    req_json = {'ip_addr': f'{ip_addr()}'}
    resp = requests.post(url=f'{sso_server}/check', json=req_json)
    log.debug(f'LOGIN CHECK. \n\taddr: {sso_server}/check\n\tresp: {resp}')
    if resp.status_code == 200:
        resp_json=resp.json()
        log.debug(f'LOGIN GET. resp_json: {resp_json}')
        if 'status' in resp_json and resp_json['status'] == 200:
            json_user = resp_json['user']
            log.info(f'LOGIN GET. json_user: {json_user}')
            session['username'] = json_user['login_name']
            user = SSO_User().get_user_by_name(json_user)
            login_user(user)
        else:
            log.info(f'----------------\n\tUSER {ip_addr()} not Registred\n----------------')
            return render_template('login.html')



@app.route('/')
def view_root():
    if g and g.user.is_anonymous:
        # LOGIN with session variable
        log.info(f'Use session variable for login ...')
    # If session variable empty then try_auto_login
    if 'username' not in session:
        try_auto_login()
    if 'list_bd' not in session or type(session['list_bd']) is not list or len(session['list_bd'])<4:
        session['list_bd'] = get_list_birthdate()    
        log.info(f'----------\nVIEW ROOT. RELOAD LIST BIRTHDATES: TYPE: {type(session['list_bd'])}. '
                  f'LEN: {len(session['list_bd'])}. FIRST VALUE: {session['list_bd']}\n----------')
    else:
        log.info(f'----------\nVIEW ROOT. LIST BIRTHDATES EXIST\n\tType: {type(session['list_bd'])} / {len(session['list_bd'])} строк\n\t{session['list_bd'][0]}\n----------')
    all_mess = get_all_message()
    # return render_template("index.html", list_bd=[], all_mess=all_mess)
    return render_template("index.html", list_bd=session['list_bd'], all_mess=all_mess)


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
        # if 'head_name' in request.form:
        #     head_name = request.form['head_name']
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
            # if message=='Success':
            #     return redirect(url_for('view_list_time_off'))            
    if message == 'Success':
        message = 'Регистрация завершена успешно'
    elif message:
        log.error(f'VIEW_TIME_OFF. ERROR: {message}')
    # return render_template("time_off.html", message = message, list_heads=list_heads)
    all_mess = get_all_message()
    return render_template("time_off.html", message = message, all_mess=all_mess)


@app.route('/secure-time-off', methods=['GET','POST'])
@login_required
def view_secure_time_off():
    log.info(f'VIEW_SECURE_TIME_OFF for {session['username']}')
    # list_heads = get_list_head()
    message = ''
    if request.method == 'POST':
        employee = request.form['employee']
        dep_name = request.form['dep_name']
        post = request.form['post']
        date_out = request.form['date_out'].replace('T',' ',1)
        date_in = request.form['date_in'].replace('T',' ',1)
        cause = request.form['cause']

        if not employee:
            message = ' ! Не указан сотрудник'
        if not dep_name:
            message = ' ! Не указан департамент'
        if not post:
            message = ' ! Не указана должность'
        if not date_out:
            message = ' ! Не указано время ухода'
        if not date_in:
            message = ' ! Не указано время прихода'
        if not cause:
            message = ' ! Не указана причина ухода'
        
        if not message:
            log.info(f"VIEW_SECURE_TIME_OFF. date_out: {date_out}, date_in: {date_in}, "
                        f"\n\temployee: {employee}\n\tpost: {post}\n\tdep_name: {dep_name}\n\tcause: {cause}, СБ: {session['full_name']}")
            message = add_secure_time_off(date_out, date_in, employee, post, dep_name, cause, session['full_name'])
            return redirect(url_for('view_secure_list_time_off'))            
    if message == 'Success':
        message = 'Регистрация завершена успешно'
    elif message:
        log.error(f'VIEW_SECURE_TIME_OFF. ERROR: {message}')
    # return render_template("time_off.html", message = message, list_heads=list_heads)
    all_mess = get_all_message()
    return render_template("secure_time_off.html", message = message, all_mess=all_mess)


@app.route('/list-time-off')
@login_required
def view_list_time_off():
    log.debug(f'VIEW LIST TIME OFF. username {session['full_name']}, admin: {session['admin']}')
    list_time_off = get_list_time_off(session['full_name'])
    all_mess = get_all_message()
    return render_template("list_time_off.html", list_time_off=list_time_off, all_mess=all_mess)


@app.route('/list-absent')
@login_required
def view_list_absent():
    log.debug(f'VIEW LIST ABSENT. username {session['full_name']}, admin: {session['admin']}')
    list_absent = get_list_absent()
    all_mess = get_all_message()
    return render_template("list_absent.html", list_absent=list_absent, all_mess=all_mess)


@app.route('/all-list-time-off', methods=['GET','POST'])
@login_required
def view_all_list_time_off():
    if 'stmt_list' in session:
        session.pop('stmt_list')

    log.debug(f'VIEW LIST TIME OFF. username {session['full_name']}, admin: {session['admin']}')
    if 'flt_month' not in session:
        session['flt_month'] = str(date.today())[0:7]
    if request.method == 'POST':
        flt_month = request.form['flt_month']  
        log.info(f' FLT_MONTH: {flt_month} : {type(flt_month)}')
        session['flt_month'] = flt_month
    list_time_off, stmt_list = get_all_list_time_off(g.user, f'{session['flt_month']}-01')
    session['stmt_list'] = stmt_list
    all_mess = get_all_message()
    return render_template("list_all_time_off.html", list_time_off=list_time_off, flt_month=session['flt_month'], all_mess=all_mess)


@app.route('/list-to-approve', methods=['GET','POST'])
@login_required
def view_list_approve():
    log.debug(f'VIEW LIST APPROVE. username {g.user.username} / {g.user.dep_name} / {g.user.principalName}')
    # log.debug(f'VIEW LIST APPROVE. dep_name: {session['dep_name']} : {type(session['dep_name'])}')
    # list_approve = get_list_to_approve(session['dep_name'], session['approve_admin'])
    list_approve = get_list_to_approve(g.user)
    all_mess = get_all_message()
    return render_template("list_approve.html", list_approve=list_approve, all_mess=all_mess)

@app.route('/secure-list-time-off', methods=['GET','POST'])
@login_required
def view_secure_list_time_off():
    log.debug(f'VIEW LIST APPROVE. username {session['full_name']}, admin: {session['admin']}')
    log.debug(f'VIEW LIST APPROVE. dep_name: {session['dep_name']} : {type(session['dep_name'])}')
    secure_list = get_secure_list_to_approve()
    all_mess = get_all_message()
    return render_template("secure_list_time_off.html", secure_list=secure_list, all_mess=all_mess)


@app.route('/approve-time-off/<int:id_reg>', methods=['GET','POST'])
@login_required
def view_approve_time_off(id_reg):
    log.debug(f'VIEW . username {session['username']}')
    approve_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_approve'))


@app.route('/refuse-time-off/<int:id_reg>', methods=['GET','POST'])
@login_required
def view_refuse_time_off(id_reg):
    log.debug(f'VIEW HEADS. username {session['username']}')
    refuse_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_approve'))


@app.route('/fact-time-off/<int:id_reg>')
@login_required
def view_fact_time_off(id_reg):
    log.debug(f'FACT TIME OFF. username {session['username']}')
    fact_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_time_off'))


@app.route('/del-from-list-time-off/<int:id_reg>')
@login_required
def view_del_from_list_time_off(id_reg):
    log.debug(f'VIEW LIST TIME_OFF. username {session['username']}')
    del_time_off(id_reg, session['full_name'])
    return redirect(url_for('view_list_time_off'))


@app.route('/new-message', methods=['GET','POST'])
@login_required
def view_new_message():
    log.debug(f'VIEW NEW MESSAGE. username {session['username']}')
    if request.method == 'POST':
        mess = request.form['new-message']
                
        log.debug(f"VIEW NEW MESSAGE. new_mess: {mess}")
        add_message(session['full_name'], session['dep_name'], mess)
        return redirect(url_for('view_root'))
    all_mess = get_all_message()
    return render_template("new_message.html", all_mess=all_mess)


@app.route('/heads', methods=['GET','POST'])
@login_required
def view_heads():
    log.debug(f'VIEW HEADS. username {session['username']}')
    list_heads = get_list_head()
    if request.method == 'POST':
        head_name = request.form['head_name']
                
        log.debug(f"VIEW_TIME-OFF. head_name: {head_name}\n\tlist_head: {list_heads}")
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
    log.debug(f"Set language. LANG: {lang}")
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

    if 'stmt_list' in session:
        do_report(session['flt_month'], file_name, session['stmt_list'])
        log.debug(f"UPLOADED_FILE. REPORT_PATH: {REPORT_PATH} FILE_NAME: {file_name}")
        return send_from_directory(REPORT_PATH, file_name)
    return redirect(url_for('view_root'))


@app.route('/phone')
def uploaded_phone():
    file_name = 'PhoneRefer.xlsx'
    do_report(session['flt_month'], file_name)
    log.debug(f"UPLOADED_FILE. REPORT_PATH: {REPORT_PATH} FILE_NAME: {file_name}")
    return send_from_directory(REPORT_PATH, file_name)
    # return redirect(url_for('view_running_reports'))


@app.route('/change-style')
def change_style():
    if 'style' in session:
        for style in styles:
            if style!=session['style']:
                session['style']=style
                break
    else: 
        session['style']=styles[0]
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set style {session['style']}. Next page: {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/list-all-employers')
def list_all_employer():
        return get_all_employers(), 200

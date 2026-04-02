import json
import gigachat
from datetime import date, datetime
from urllib.parse import urlparse
from sqlalchemy.orm import joinedload, subqueryload, with_loader_criteria
from sqlalchemy import func
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from flask_login import login_user, logout_user
from database import db
from settings import app, login_manager, bcrypt
from flask_login import login_required, current_user
from models import *
import random



gigachat_auth_key = 'MDE5YjAzNDMtZDM0Zi03M2Q2LWE2MmQtNzJhMmYzZTU3ODRiOjRlYjg4Y2QyLTdlZDYtNDkxZS1iZmJmLTVkOTNjZTE3M2NlMA=='
gigachat_client_id = '019b0343-d34f-73d6-a62d-72a2f3e5784b'
gigachat_scope = 'GIGACHAT_API_PERS'
indeicator_set_key = 'fcff5cf3-723b-4a83-943f-8badbe6e33a1'

giga = gigachat.GigaChat(
    credentials=gigachat_auth_key,
    scope=gigachat_scope,
    model="GigaChat",
    verify_ssl_certs=False,
)


@app.template_filter('datetime')
def datetime_filter(value, format='%d.%m.%Y'):
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    return str(value)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    target_url = urlparse(target)
    
    return ((target_url.scheme in ('http', 'https') and
             target_url.netloc == ref_url.netloc) or
            (target_url.netloc == '' or target_url.scheme == ''))

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == int(user_id)).first()

@app.route('/', methods=['get'])
def index():
    return render_template('glav.html')

@app.route('/devices', methods=['get'])
@login_required
def devices():
    devices = db.session.query(Device).all()
    return render_template('devices.html', devices=devices)

@app.route('/include-device/<int:user_id>/<int:device_id>', methods=['post'])
@login_required
def include_device(user_id, device_id):
    user = db.session.query(User).filter(User.id==user_id).first()
    device = db.session.query(Device).filter(Device.id==device_id).first()

    if not user or not device:
        abort(404, 'Пользователь или прибор учета не найден!')
    
    user_device = db.session.query(UserDevice).filter(UserDevice.user_id==user_id, UserDevice.device_id==device_id).first()
    if user_device:
        abort(409, 'Такой прибор учета уже у вас имеется!')
    
    user_device = UserDevice()
    user_device.user_id = user_id
    user_device.device_id = device_id
    user_device.number = ''
    db.session.add(user_device)
    db.session.commit()

    return redirect(url_for('my_devices', user_id=user_id))

@app.route('/mydevices/<int:user_id>', methods=['get'])
@login_required
def my_devices(user_id):
    devices = db.session.query(UserDevice).options(joinedload(UserDevice.device)).filter(UserDevice.user_id==user_id).all()
    return render_template('mydevices.html', mydevices=devices)

@app.route('/mydevice/<int:user_id>/<int:device_id>', methods=['get', 'post'])
@login_required
def my_device(user_id, device_id):
    print(user_id, device_id)
    user_device = db.session.query(UserDevice).filter(UserDevice.user_id==user_id, UserDevice.device_id==device_id).first()
    print(user_device.user_id, user_device.device_id)
    if not user_device:
        abort(404, 'Прибор учета не найден!')
    if request.method == 'POST':
        user_device.number = request.form['number']
        print(user_device.user_id, user_device.device_id, user_device.number)
        db.session.commit()
        return redirect(url_for('my_devices', user_id=user_id))
    return render_template('mydevice.html', mydevice=user_device)

@app.route('/indicators/<int:mydevice_id>', methods=['get', 'post'])
@login_required
def indicators(mydevice_id):
    my_device = db.session.query(UserDevice).options(joinedload(UserDevice.indicators), joinedload(UserDevice.device)).filter(UserDevice.id==mydevice_id).first()
    if not my_device:
        abort(404, 'Прибор учета не найден!')
    return render_template('indicators.html', mydevice=my_device, indicators=my_device.indicators)

@app.route('/profile', methods=['get', 'post'])
@login_required
def profile():
    print(request.method)
    error = ''
    success = ''
    if request.method == "POST":
        print('got post request')
        fullname = request.form['fullname']
        user_login = request.form['login']
        pwd = request.form['password']
        pwd1 = request.form['password1']
        user=db.session.query(User).filter(User.login==user_login).first()

        print(user, fullname, pwd, pwd1)

        if user is None:
            error = 'Такой пользователь не существует!'
        elif pwd != pwd1:
            error = 'Подтверждение пароля не свопадает с паролем!'
        else:
            user.fullname = fullname
            if pwd != '' and pwd1 != '':
                user.password = pwd
            db.session.commit()
            success = 'Профиль успешно изменен!'
    return render_template('profile.html', error=error, success=success, user=current_user)

@app.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        user_login = request.form['login']
        pwd = request.form['password']
        user = db.session.query(User).filter(User.login == user_login).first()
        print(user, pwd)
        print(user.password)
        print(bcrypt.check_password_hash(user.password, pwd))
        if user and bcrypt.check_password_hash(user.password, pwd):
            login_user(user)
            next_url = request.form.get('next_url')
            if not next_url or not is_safe_url(next_url):
                return redirect(url_for('index'))
            else:
                return redirect(next_url)
    return render_template('login.html')

@app.route('/logout', methods=['post'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
    success = ""
    error = ""
    if request.method == 'POST':
        user_login = request.form['login']
        fullname = request.form['fullname']
        pwd = request.form['password']
        pwd1 = request.form['password1']
        user=db.session.query(User).filter(User.login==user_login).first()
        if user is not None:
            error = 'Такой пользователь уже существует!'
        elif pwd != pwd1:
            error = 'Подтверждение пароля не свопадает с паролем!'
        else:
            print('creating user')
            user = User()
            user.fullname = fullname
            user.login = user_login
            user.password = pwd
            db.session.add(user)
            db.session.commit()
            success = "Профиль успешно создан!"
            return redirect(url_for('login'))
    return render_template('register.html', error=error, success=success)

@app.route('/forecast/<string:number>', methods=['post'])
@login_required
def forecast(number):
    prompt = '''У меня есть текстовые данные в формате:
                дата (DD.MM.YYYY), серийный номер, значение
                Считай, что для каждого серийного номера это временной ряд по дням.
                Выполни прогноз на 1 месяц вперёд для значений.
                Не используй сложные модели — можешь применить простой тренд/среднее/экспоненциальное сглаживание.
                Представь результат так: 
                30 дат (1–30‑е число следующего месяца) и прогнозные значения.
                Формат вывода данных: дата1;прогнозное значение1;дата2;прогнозное значение2;дата3;прогнозное значение3; и т.д.
                В качестве разделителей используй только точкаи с запятой.
                Не включай в данные серийный номер.
                Выведи только результаты без объяснений\n'''
    user_device_indicators = db.session.query(Indicator)\
                             .outerjoin(UserDevice, Indicator.user_device_id==UserDevice.id)\
                             .filter(UserDevice.number==number)\
                             .options(joinedload(Indicator.user_device))\
                             .order_by(Indicator.create_date.desc())\
                             .limit(30).all()
    month_indicators = [','.join([indicator.create_date.strftime("%d.%m.%Y"), indicator.user_device.number, str(indicator.value)]) for indicator in user_device_indicators]
    prompt += '\n'.join(month_indicators)
    result = giga.chat(prompt)
    if result is not None and result.choices[0].message.content is not None:
        print(result.choices[0].message.content)
        giga_answer = result.choices[0].message.content.split(';')
        it = iter(giga_answer)
        forecast = list(zip(it, it))
        return render_template('forecast.html', forecast=forecast)
    return render_template('forecast.html', error='Ответ от Гигачата не получен, к сожалению!')

@app.route('/setindicator', methods=['post'])
def set_indicator():
    if request.method == 'POST':
        data = request.json
        print(data)
        if not data or 'key' not in data or data['key'] != indeicator_set_key:
            abort(404)
        number = data['number']
        ind_date = data['date']
        value = data['value']

        user_device = db.session.query(UserDevice).filter(UserDevice.number==number).first()
        if not user_device:
            return jsonify({'result': False, 'answer':'Устройство не найдено!'})
        
        indicator = Indicator()
        indicator.create_date = datetime.datetime.strptime(ind_date, '%d.%m.%Y').date()
        indicator.user_device_id = user_device.id
        indicator.value = int(value)
        user_device.indicators.append(indicator)
        db.session.commit()

        return jsonify({'result': True, 'answer': 'Показатели приняты'})
    return jsonify({'result': False})

@app.route("/vacuum")
def vacuum_control():
    return render_template("vacuum.html")
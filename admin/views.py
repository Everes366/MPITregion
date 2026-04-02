from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from wtforms import SelectField
from models import DeviceType


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class UserView(ModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_list = (
        'id',
        'fullname',
        'login',
        'is_admin'
        )
    form_columns = [
        'fullname',
        'login',
        'password',
        'is_admin'
        ]
    column_details_list = (
        'id',
        'fullname',
        'login',
        'password',
        'is_admin'
        )


class DeviceView(ModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_list = (
        'id',
        'name',
        'type',
        'file'
        )
    form_columns = [
        'name',
        'type',
        'file'
        ]
    column_details_list = (
        'id',
        'name',
        'type',
        'file'
        )
    
    form_overrides = {
        'type': SelectField  # ← ДОБАВЬТЕ ЭТО
    }

    form_args = {
        'type': {
            'choices': [(member.name, member.value) for member in DeviceType]
        }
    }
    
    form_widget_args = {
        'type': {'class': 'form-control'}  # стилизация
    }